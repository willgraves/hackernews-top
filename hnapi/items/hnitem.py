"""Abstract Hacker News Item

Author: Rylan Santinon
"""

from abc import ABCMeta, abstractmethod

#pylint: disable=abstract-class-not-used
class HnItem(object):
    """Abstract item"""
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_schema(self):
        """Return the item's schema"""
        pass

    def is_deleted(self):
        """Return True if this item is deleted"""
        #pylint: disable=no-member
        return not not self.json.get('deleted') or \
                not not self.json.get('dead')

    def get_field_by_name(self, name):
        """Get field by name

        Parameters
        ----------
        name : str
            The name of the field

        Returns
        -------
        str
            The value held in the field

        Raises
        ------
        RuntimeError
            if `name` is not in the schema
        """
        #pylint: disable=no-member
        schema = self.get_schema()
        if schema.has_field(name):
            return self.json[name]
        else:
            raise RuntimeError("No field named %r in %r" \
                    % (name, schema))

    def get(self, name):
        """Same as get_field_by_name"""
        return self.get_field_by_name(name)

    @abstractmethod
    def __repr__(self):
        pass
