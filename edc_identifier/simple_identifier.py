import random

from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist


class DuplicateIdentifierError(Exception):
    pass


class SimpleIdentifier:

    random_string_length = 5
    template = '{device_id}{random_string}'

    def __init__(self, template=None, random_string_length=None):
        edc_device_app_config = django_apps.get_app_config('edc_device')
        self.template = template or self.template
        self.random_string_length = random_string_length or self.random_string_length
        device_id = edc_device_app_config.device_id
        self.identifier = self.template.format(
            device_id=device_id, random_string=self.random_string)

    def __str__(self):
        return self.identifier

    @property
    def random_string(self):
        return ''.join(
            [random.choice('ABCDEFGHKMNPRTUVWXYZ2346789') for _ in range(
                self.random_string_length)])


class SimpleUniqueIdentifier:

    """Usage:

        class ManifestIdentifier(Identifier):
            random_string_length = 9
            identifier_attr = 'manifest_identifier'
            template = 'M{device_id}{random_string}'
    """

    random_string_length = 5
    identifier_type = 'simple_identifier'
    identifier_attr = 'identifier'
    model = 'edc_identifier.identifierhistory'
    template = '{device_id}{random_string}'
    identifier_cls = SimpleIdentifier

    def __init__(self, model=None, identifier_attr=None, identifier_type=None):
        self._identifier = None
        self.model = model or self.model
        self.identifier_attr = identifier_attr or self.identifier_attr
        self.identifier_type = identifier_type or self.identifier_type
        self.identifier_obj = self.identifier_cls(
            template=self.template,
            random_string_length=self.random_string_length)
        self.model_cls.objects.create(
            identifier_type=self.identifier_type,
            **{self.identifier_attr: self.identifier})

    @property
    def identifier(self):
        if not self._identifier:
            identifier = self._get_new_identifier()
            tries = 1
            while True:
                tries += 1
                try:
                    self.model_cls.objects.get(
                        identifier_type=self.identifier_type,
                        ** {self.identifier_attr: identifier})
                except ObjectDoesNotExist:
                    break
                else:
                    identifier = self._get_new_identifier()
                if tries == len('ABCDEFGHKMNPRTUVWXYZ2346789') ** self.random_string_length:
                    raise DuplicateIdentifierError(
                        'Unable prepare a unique identifier, '
                        'all are taken. Increase the length of the random string')
            self._identifier = identifier
        return self._identifier

    def _get_new_identifier(self):
        """Returns a new identifier.
        """
        identifier_obj = self.identifier_cls(
            template=self.template,
            random_string_length=self.random_string_length)
        return identifier_obj.identifier

    @property
    def model_cls(self):
        return django_apps.get_model(self.model)
