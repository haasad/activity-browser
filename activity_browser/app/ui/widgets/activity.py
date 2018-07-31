# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtWidgets

from .line_edit import SignalledLineEdit, SignalledPlainTextEdit


class DetailsGroupBox(QtWidgets.QGroupBox):
    def __init__(self, label, widget):
        super().__init__(label)
        self.widget = widget
        self.setCheckable(True)
        self.toggled.connect(self.showhide)
        self.setChecked(False)
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(widget)
        self.setLayout(layout)
        if isinstance(self.widget, QtWidgets.QTableWidget):
            self.widget.itemChanged.connect(self.toggle_empty_table)

    def showhide(self):
        self.widget.setVisible(self.isChecked())

    def toggle_empty_table(self):
        self.setChecked(bool(self.widget.rowCount()))


class ActivityDataGrid(QtWidgets.QWidget):
    """ Displayed at the top of each activity panel to show the user basic data related to the activity
    Expects to find the following data for each activity displayed: name, location, database, comment
    Exchange data is displayed separately, below this grid, in tables.
    Includes the read-only checkbox which enables or disables user-editing of some activity and exchange data
    """
    def __init__(self, parent=None, activity=None, read_only=True):
        super(ActivityDataGrid, self).__init__(parent)
        self.activity = activity
        self.read_only = read_only

        self.name_box = SignalledLineEdit(
            key=getattr(self.activity, "key", None),
            field="name",
            parent=self,
        )
        self.name_box.setPlaceholderText("Activity name")

        #improvement todo: location to be selectable from dropdown rather than free-text
        #but this requires forming a list of valid locations based on selected db..

        self.location_box = SignalledLineEdit(
            key=getattr(self.activity, "key", None),
            field="location",
            parent=self,
        )
        self.location_box.setPlaceholderText("ISO 2-letter code or custom name")

        #improvement todo: allow user to copy open activity to other db, via drop-down menu here
        self.database = QtWidgets.QLabel('')

        self.comment_box = SignalledPlainTextEdit(
            key=getattr(self.activity, "key", None),
            field="comment",
            parent=self,
        )
        self.comment_groupbox = DetailsGroupBox(
            'Description', self.comment_box)
        self.comment_groupbox.setChecked(False)

        # do not allow user to edit fields if the activity is read-only
        self.set_activity_fields_read_only(read_only=self.read_only)

        # arrange widgets for display as a grid
        self.grid = QtWidgets.QGridLayout()
        self.grid.setSpacing(5)
        self.grid.setAlignment(QtCore.Qt.AlignTop)

        self.grid.addWidget(QtWidgets.QLabel('Name'), 1, 1)
        self.grid.addWidget(self.name_box, 1, 2, 1, 3)
        self.grid.addWidget(QtWidgets.QLabel('Location'), 2, 1)
        self.grid.addWidget(self.location_box, 2, 2, 1, -1)
        self.grid.addWidget(self.database, 3, 2, 1, -1)
        self.grid.addWidget(QtWidgets.QLabel('Database'), 3, 1)
        self.grid.addWidget(self.comment_groupbox, 4, 1, 2, -1)

        self.setLayout(self.grid)

        if activity:
            self.populate()

    def set_activity_fields_read_only(self, read_only=True):
        # called on init after widgets instantiated
        # also whenever a user clicks the read-only checkbox
        self.read_only = read_only
        # user cannot edit these fields if they are read-only
        self.name_box.setReadOnly(self.read_only)
        self.location_box.setReadOnly(self.read_only)
        # self.database.setReadOnly(self.read_only) # read-only already for now
        self.comment_box.setReadOnly(self.read_only)

    def populate(self, activity=None):
        if activity:
            self.activity = activity

        self.database.setText(self.activity['database'])
        self.name_box.setText(self.activity['name'])
        self.name_box._key = self.activity.key
        self.location_box.setText(self.activity.get('location', ''))
        self.location_box._key = self.activity.key
        self.comment_box.setPlainText(self.activity.get('comment', ''))
        self.comment_box._key = self.activity.key
        # the <font> html-tag has no effect besides making the tooltip rich text
        # this is required for line breaks of long comments
        self.comment_groupbox.setToolTip(
            '<font>{}</font>'.format(self.comment_box.toPlainText())
        )
        self.comment_box._before = self.activity.get('comment', '')
        self.comment_box.adjust_size()
