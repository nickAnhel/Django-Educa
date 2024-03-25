from django.apps import apps
from django.forms import modelform_factory
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.shortcuts import redirect, get_object_or_404
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic.base import View, TemplateResponseMixin

from .models import Course, Module, Content, ItemBase
from .forms import ModuleFormSet


class OwnerMixin:
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(owner=self.request.user)


class OwnerEditMixin(OwnerMixin):
    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class OwnerCourseMixin(OwnerMixin, LoginRequiredMixin, PermissionRequiredMixin):
    model = Course
    fields = ["subject", "title", "slug", "overview"]
    success_url = reverse_lazy("manage_course_list")


class OwnerCourseEditMixin(OwnerCourseMixin, OwnerEditMixin):
    template_name = "courses/manage/course/form.html"


class ManageCourseListView(OwnerCourseMixin, ListView):
    template_name = "courses/manage/course/list.html"
    permission_required = "courses.view_course"


class CourseCreateView(OwnerCourseEditMixin, CreateView):
    permission_required = "courses.add_course"


class CourseUpdateView(OwnerCourseEditMixin, UpdateView):
    permission_required = "courses.change_course"


class CourseDeleteView(OwnerCourseMixin, DeleteView):
    template_name = "courses/manage/course/delete.html"
    permission_required = "courses.delete_course"


class CourseModuleUpdateView(TemplateResponseMixin, View):
    template_name = "courses/manage/module/formset.html"
    course = None

    def get_formset(self, data=None):
        return ModuleFormSet(instance=self.course, data=data)

    def dispatch(self, request: HttpRequest, pk) -> HttpResponse:
        self.course = get_object_or_404(Course, id=pk, owner=request.user)
        return super().dispatch(request, pk)

    def get(self, request: HttpRequest, *args, **kwargs):
        formset = self.get_formset()
        return self.render_to_response({"course": self.course, "formset": formset})

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponseRedirect | HttpResponse:
        formset = self.get_formset(data=request.POST)
        if formset.is_valid():
            formset.save()
            return redirect("manage_course_list")
        return self.render_to_response({"course": self.course, "formset": formset})


class ContentCreateUpdateView(TemplateResponseMixin, View):
    module: Module = None
    model: ItemBase = None
    obj = None
    template_name = "courses/manage/content/form.html"

    def get_model(self, model_name):
        if model_name in ["text", "file", "image", "video"]:
            return apps.get_model(app_label="courses", model_name=model_name)
        return None

    def get_form(self, model, *args, **kwargs):
        form = modelform_factory(model=model, exclude=["owner", "order", "created", "updated"])
        return form(*args, **kwargs)

    def dispatch(self, request: HttpRequest, module_id: int, model_name: str, obj_id: int = None) -> HttpResponse:
        self.module = get_object_or_404(Module, id=module_id, course__owner=request.user)
        self.model = self.get_model(model_name)

        if obj_id:
            self.obj = get_object_or_404(self.model, id=obj_id)

        return super().dispatch(request, module_id, model_name, obj_id)

    def get(self, request: HttpRequest, module_id: int, model_name: str, obj_id: int = None) -> HttpResponse:
        form = self.get_form(self.model, instance=self.obj)
        return self.render_to_response({"form": form, "object": self.obj})

    def post(self, request: HttpRequest, module_id: int, model_name: str, obj_id: int = None) -> HttpResponse:
        form = self.get_form(self.model, intance=self.obj, data=request.POST, files=request.FILES)

        if form.is_valid():
            obj = form.save(commit=False)
            obj.owmer = request.user
            obj.save()

            if not obj_id:
                Content.objects.create(modile=self.module, item=obj)

            return redirect("module_content_list", self.module.id)

        return self.render_to_response({"form": form, "object": self.obj})


class ContentDeleteView(View):
    def post(self, request: HttpRequest, content_id: int) -> HttpResponseRedirect:
        content = get_object_or_404(Content, id=content_id, module__course__owner=request.user)
        module = content.module
        content.item.delete()
        content.delete()
        return redirect("module_content_list", module.id)
