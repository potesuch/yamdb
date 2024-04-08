from rest_framework import mixins


class ListCreateDestroyMixin(mixins.ListModelMixin, mixins.CreateModelMixin,
                             mixins.DestroyModelMixin):
    pass
