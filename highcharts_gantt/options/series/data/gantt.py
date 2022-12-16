from typing import Optional
from decimal import Decimal
from datetime import datetime

from validator_collection import validators, checkers

from highcharts_python.options.series.data.base import DataBase

from highcharts_gantt import errors, constants
from highcharts_gantt.decorators import validate_types
from highcharts_gantt.metaclasses import HighchartsMeta
from highcharts_gantt.utility_functions import validate_color


class ProgressIndicator(HighchartsMeta):
    """Object representing the progress completed within a data point."""

    def __init__(self, **kwargs):
        self._amount = None
        self._fill = None

        self.amount = kwargs.get('amount', None)
        self.fill = kwargs.get('fill', None)

    @property
    def amount(self) -> Optional[int | float | Decimal]:
        """The amount completed in the progress indicator, ranging from ``0`` (not
        started) to ``1`` (completed). Defaults to :obj:`None <python:None>`, which
        behaves as ``0``.

        :rtype: numeric or :obj:`None <python:None>`
        """
        return self._amount

    @amount.setter
    def amount(self, value):
        self._amount = validators.numeric(value,
                                          allow_empty = True,
                                          minimum = 0,
                                          maximum = 1)

    @property
    def fill(self) -> Optional[str | Gradient | Pattern]:
        """Fill color to apply to the completion portion. Defaults to
        :obj:`None <python:None>`, which will apply a darkened variant of the data point's
        color.

        :rtype: :obj:`None <python:None>`, :class:`Gradient`, or :class:`Pattern`
        """
        return self._fill

    @fill.setter
    def fill(self, value):
        self._fill = validate_color(value)

    @classmethod
    def _get_kwargs_from_dict(cls, as_dict):
        kwargs = {
            'amount': as_dict.get('amount', None),
            'fill': as_dict.get('fill', None),
        }

        return kwargs

    def _to_untrimmed_dict(self, in_cls = None) -> dict:
        untrimmed = {
            'amount': self.amount,
            'fill': self.fill
        }

        return untrimmed


class GanttData(DataBase):
    """Data point used in a
    :class:`GanttSeries <highcharts_gantt.options.series.gantt.GanttSeries>`.
    """

    def __init__(self, **kwargs):
        self._collapsed = None
        self._completed = None
        self._dependency = None
        self._end = None
        self._milestone = None
        self._parent = None
        self._start = None
        self._y = None

        self.collapsed = kwargs.get('collapsed', None)
        self.completed = kwargs.get('completed', None)
        self.dependency = kwargs.get('dependency', None)
        self.end = kwargs.get('end', None)
        self.milestone = kwargs.get('milestone', None)
        self.parent = kwargs.get('parent', None)
        self.start = kwargs.get('start', None)
        self.y = kwargs.get('y', None)

        super().__init__(**kwargs)

    @property
    def collapsed(self) -> Optional[bool]:
        """If ``True``, collapses the grid node belonging to this data point. Defaults to
        ``False``.

        .. note::

          Respected in axes of type ``'treegrid'``.

        :rtype: :class:`bool <python:bool>` or :obj:`None <python:None>`
        """
        return self._collapsed

    @collapsed.setter
    def collapsed(self, value):
        if value is None:
            self._collapsed = None
        else:
            self._collapsed = bool(value)

    @property
    def completed(self) -> Optional[int | float | Decimal | ProgressIndicator]:
        """Configuration of a progress indicator for the data point. Accepts either a
        numeric value between ``0`` (no progress) to ``1`` (fully complete) or a
        :class:`ProgressIndicator` object. Defaults to :obj:`None <python:None>`.

        .. note::

          If supplied as a number, will fill in the completed portion with a darkened
          version of the main color.

        :rtype: numeric or :obj:`ProgressIndicator` or :obj:`None <python:None>`
        """
        return self._completed

    @completed.setter
    def completed(self, value):
        if value is None:
            self._completed = None
        else:
            try:
                value = validators.numeric(value,
                                           allow_empty = False,
                                           minimum = 0,
                                           maximum = 1)
            except (ValueError, TypeError):
                value = validate_types(value, ProgressIndicator)

            self._completed = value

    @property
    def dependency(self) -> Optional[DataConnection | str | List[DataConnection | str]]:
        """Indicates data points that this data point depends on.

        Accepts either a :class:`str <python:str>` which corresponds to the ID of a
        different data point, a
        :class:`DataConnection <highcharts_gantt.options.series.data.connect.DataConnection>`
        object configuring the connection, an array of either, or
        :obj:`None <python:None>`. Defaults to :obj:`None <python:None>`

        :rtype: :class:`str <python:str>` or
          :class:`DataConnection <highcharts_gantt.options.series.data.connect.DataConnection>`
          or an iterable of :class:`str <python:str>` or
          :class:`DataConnection <highcharts_gantt.options.series.data.connect.DataConnection>`
          or :obj:`None <python:None>`
        """
        return self._connect

    @dependency.setter
    def dependency(self, value):
        if not value:
            self._dependency = None
        else:
            if not checkers.is_iterable(value, forbid_literals = (str, bytes, dict)):
                try:
                    value = validators.string(value)
                except (ValueError, TypeError):
                    value = validate_types(value, DataConnection)

                self._dependency = value
            else:
                processed_value = []
                for item in value:
                    try:
                        item = validators.string(item)
                    except (ValueError, TypeError):
                        item = validate_types(item, DataConnection)
                    processed_value.append(item)

                self._dependency = [x for x in processed_value]

    @property
    def end(self) -> Optional[datetime]:
        """The end time of the data point (task).

        .. note::

          While **Highcharts Gantt for Python** represents this value as a
          :class:`datetime <python:datetime.datetime>`, it actually represents a POSIX
          timestamp (number of milliseconds since January 1, 1970). If you supply a
          numerical value, it will be converted to a
          :class:`datetime <python:datetime.datetime>`, and when serialized back to
          JavaScript object literal notation it will be converted back to a numerical
          value.

        :rtype: :class:`datetime <python:datetime.datetime>` or :obj:`None <python:None>`
        """
        return self._end

    @end.setter
    def end(self, value):
        self._end = validators.datetime(value, allow_empty = True, coerce_value = True)

    @property
    def milestone(self) -> Optional[bool]:
        """If ``True``, indicates that this task (data point) is a milestone, which means
        that only the
        :meth:`.start <highcharts_gantt.options.series.data.gantt.GanttData.start>`
        property is taken into consideration and the
        :meth:`.end <highcharts_gantt.options.series.data.gantt.GanttData.end>` property
        is ignored. Defaults to :obj:`None <python:None>`, which behaves as ``False``.

        :rtype: :class:`bool <python:bool>` or :obj:`None <python:None>`
        """
        return self._milestone

    @milestone.setter
    def milestone(self, value):
        if value is None:
            self._milestone = None
        else:
            self._milestone = bool(value)

    @property
    def parent(self) -> Optional[str]:
        """The ID of the parent task (data point) in the Gantt series. Defaults to
        :obj:`None <python:None>`.

        :rtype: :class:`str <python:str>` or :obj:`None <python:None>`
        """
        return self._parent

    @parent.setter
    def parent(self, value):
        self._parent = validators.string(value, allow_empty = True)

    @property
    def start(self) -> Optional[datetime]:
        """The start time of the data point (task).

        .. note::

          While **Highcharts Gantt for Python** represents this value as a
          :class:`datetime <python:datetime.datetime>`, it actually represents a POSIX
          timestamp (number of milliseconds since January 1, 1970). If you supply a
          numerical value, it will be converted to a
          :class:`datetime <python:datetime.datetime>`, and when serialized back to
          JavaScript object literal notation it will be converted back to a numerical
          value.

        :rtype: :class:`datetime <python:datetime.datetime>` or :obj:`None <python:None>`
        """
        return self._start

    @start.setter
    def start(self, value):
        self._start = validators.datetime(value, allow_empty = True, coerce_value = True)

    @property
    def y(self) -> Optional[int | float | Decimal]:
        """The Y-axis value of the task (data point).

        :rtype: numerical or :obj:`None <python:None>`
        """
        return self._y

    @y.setter
    def y(self, value):
        self._y = validators.numeric(value, allow_empty = True)

    @classmethod
    def _get_kwargs_from_dict(cls, as_dict):
        """Convenience method which returns the keyword arguments used to initialize the
        class from a Highcharts Javascript-compatible :class:`dict <python:dict>` object.

        :param as_dict: The HighCharts JS compatible :class:`dict <python:dict>`
          representation of the object.
        :type as_dict: :class:`dict <python:dict>`

        :returns: The keyword arguments that would be used to initialize an instance.
        :rtype: :class:`dict <python:dict>`

        """
        kwargs = {
            'accessibility': as_dict.get('accessibility', None),
            'class_name': as_dict.get('className', None),
            'color': as_dict.get('color', None),
            'color_index': as_dict.get('colorIndex', None),
            'custom': as_dict.get('custom', None),
            'description': as_dict.get('description', None),
            'events': as_dict.get('events', None),
            'id': as_dict.get('id', None),
            'label_rank': as_dict.get('labelRank',
                                      None) or as_dict.get('labelrank',
                                                           None),
            'name': as_dict.get('name', None),
            'selected': as_dict.get('selected', None),

            'collapsed': as_dict.get('collapsed', None),
            'completed': as_dict.get('completed', None),
            'dependency': as_dict.get('dependency', None),
            'end': as_dict.get('end', None),
            'milestone': as_dict.get('milestone', None),
            'parent': as_dict.get('parent', None),
            'start': as_dict.get('start', None),
            'y': as_dict.get('y', None),
        }

        return kwargs

    def _to_untrimmed_dict(self, in_cls = None) -> dict:
        untrimmed = {
            'collapsed': self.collapsed,
            'completed': self.completed,
            'dependency': self.dependency,
            'end': None,
            'milestone': self.milestone,
            'parent': self.parent,
            'start': None,
            'y': self.y
        }

        if self.end is not None:
            untrimmed['end'] = self.end.timestamp()
        if self.start is not None:
            untrimmed['start'] = self.start.timestamp()

        parent_as_dict = super()._to_untrimmed_dict(in_cls = in_cls)
        for key in parent_as_dict:
            untrimmed[key] = parent_as_dict[key]

        return untrimmed

    @classmethod
    def from_array(cls, value):
        """Creates a collection of data point instances, parsing the contents of ``value``
        as an array (iterable). This method is specifically used to parse data that is
        input to **Highcharts for Python** without property names, in an array-organized
        structure as described in the `Highcharts JS <https://www.highcharts.com>`__
        documentation.

          .. seealso::

            The specific structure of the expected array is highly dependent on the type
            of data point that the series needs, which itself is dependent on the series
            type itself.

            Please review the detailed :ref:`series documentation <series_documentation>`
            for series type-specific details of relevant array structures.

          .. note::

            An example of how this works for a simple
            :class:`LineSeries <highcharts_python.options.series.area.LineSeries>` (which
            uses
            :class:`CartesianData <highcharts_python.options.series.data.cartesian.CartesianData>`
            data points) would be:

            .. code-block:: python

              my_series = LineSeries()

              # A simple array of numerical values which correspond to the Y value of the
              # data point
              my_series.data = [0, 5, 3, 5]

              # An array containing 2-member arrays (corresponding to the X and Y values
              # of the data point)
              my_series.data = [
                  [0, 0],
                  [1, 5],
                  [2, 3],
                  [3, 5]
              ]

              # An array of dict with named values
              my_series.data = [
                {
                    'x': 0,
                    'y': 0,
                    'name': 'Point1',
                    'color': '#00FF00'
                },
                {
                    'x': 1,
                    'y': 5,
                    'name': 'Point2',
                    'color': '#CCC'
                },
                {
                    'x': 2,
                    'y': 3,
                    'name': 'Point3',
                    'color': '#999'
                },
                {
                    'x': 3,
                    'y': 5,
                    'name': 'Point4',
                    'color': '#000'
                }
              ]

        :param value: The value that should contain the data which will be converted into
          data point instances.

          .. note::

            If ``value`` is not an iterable, it will be converted into an iterable to be
            further de-serialized correctly.

        :type value: iterable

        :returns: Collection of :term:`data point` instances (descended from
          :class:`DataBase <highcharts_python.options.series.data.base.DataBase>`)
        :rtype: :class:`list <python:list>` of
          :class:`DataBase <highcharts_python.options.series.data.base.DataBase>`
          descendant instances
        """
        if not value:
            return []
        elif not checkers.is_iterable(value):
            value = [value]

        collection = []
        for item in value:
            if checkers.is_type(item, 'GanttData'):
                as_obj = item
            elif checkers.is_dict(item):
                as_obj = cls.from_dict(item)
            elif item is None or isinstance(item, constants.EnforcedNullType):
                as_obj = cls()
            else:
                raise errors.HighchartsValueError(f'each data point supplied must either '
                                                  f'be a GanttData Data Point or be '
                                                  f'coercable to one. Could not coerce: '
                                                  f'{item}')
            collection.append(as_obj)

        return collection