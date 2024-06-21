from rest_framework import mixins


class ListCreateDestroyMixin(mixins.ListModelMixin, mixins.CreateModelMixin,
                             mixins.DestroyModelMixin):
    """
    Комбинация mixins для предоставления функционала списка, создания и удаления объектов модели.
    """
    pass
