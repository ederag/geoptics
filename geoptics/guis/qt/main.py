# -*- coding: utf-8 -*-

# Copyright (C) 2014 ederag <edera@gmx.fr>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with GeOptics; see the file LICENSE.txt.  If not, see
# <http://www.gnu.org/licenses/>.


"""Main module for the :mod:`.guis.qt` backend.

Upon import, a QApplication instance is created,
if none is found already runnning by Qt.
The running QApplication can be accessed as :attr:`~geoptics.guis.qt.main.app`.
"""


import logging
logger = logging.getLogger(__name__)   # noqa: E402
import sys

from PyQt5.QtCore import (
	QCoreApplication,
	QPoint,
	QSettings,
	QSize,
	pyqtSlot,
	qDebug,
)
from PyQt5.QtGui import QIcon, QKeySequence
from PyQt5.QtWidgets import (
	QAction,
	QApplication,
	QErrorMessage,
	QFileDialog,
	QMainWindow,
	QMessageBox,
	QToolBar,
)

import yaml  # for load/save

from .scene import Scene
from .view import GraphicsView, GraphicsViewFrame


# initialize application for Qt
#: The Qt QApplication instance
app = QCoreApplication.instance()
if app:
	# an app was already present, just graft onto it
	# this allow to launch t_geo.py from IPython, in a non-blocking way
	app_created_here = False
else:
	# no app was present, create one
	app = QApplication(sys.argv)
	app_created_here = True

# settings will be stored in ~/.config/<org>/<app>
# see QSettings doc
# we choose org=app=geoptics
app.setOrganizationName("geoptics")
app.setOrganizationDomain("geoptics.org")  # FIXME: to be updated
app.setApplicationName("geoptics")


# main window
class Gui(QMainWindow):
	"""Principal window of the GUI."""
	
	def __init__(self):
		QMainWindow.__init__(self)
		self.setup()
		
	def setup(self):
		"""Set up the main window."""
		
		self.setWindowTitle("GeOptics")
		
		self.statusBar()
		
		self.show()
		
		self.current_filename = None
		
		# main drawing area
		self.scene = Scene()
		self.view = GraphicsView()
		self.view.setScene(self.scene.g)
		# set a default view right now,
		# so no need for the mouse to enter the view
		self.scene.g.active_view = self.view
		self.graphicsView_frame = GraphicsViewFrame(view=self.view)
		self.scene.g.signal_mouse_position_changed.connect(
		        self.graphicsView_frame.position_indicator.on_changed_position)
		self.setCentralWidget(self.graphicsView_frame)
		
		# menus
		# use theme icons whenever possible, names from
		# http://standards.freedesktop.org/icon-naming-spec/icon-naming-spec-latest.html
		
		icon = QIcon.fromTheme('document-open')
		open_action = QAction(icon, 'Open', self)
		open_action.setShortcut('Ctrl+O')
		open_action.setStatusTip('Clear scene and load from file')
		open_action.triggered.connect(self.open)
		
		icon = QIcon.fromTheme('document-open')
		import_action = QAction(icon, 'Import', self)
		import_action.setShortcut('Ctrl+I')
		import_action.setStatusTip('Import from file')
		import_action.triggered.connect(self.import_slot)
		
		icon = QIcon.fromTheme('document-save')
		save_action = QAction(icon, 'Save', self)
		save_action.setShortcut(QKeySequence.Save)
		save_action.setStatusTip('Save')
		save_action.triggered.connect(self.save)
		
		icon = QIcon.fromTheme('document-save-as')
		saveas_action = QAction(icon, 'Save As', self)
		saveas_action.setShortcut(QKeySequence.SaveAs)
		saveas_action.setStatusTip('Save As')
		saveas_action.triggered.connect(self.saveas)
		
		icon = QIcon.fromTheme('application-exit')
		exit_action = QAction(icon, 'Exit', self)
		exit_action.setShortcut(QKeySequence.Quit)
		exit_action.setStatusTip('Exit application')
		exit_action.triggered.connect(self.exit)
		
		icon = QIcon.fromTheme('text-field')
		display_action = QAction(icon, 'Display', self)
		display_action.setShortcut('Ctrl+D')
		display_action.setStatusTip('Display')
		display_action.triggered.connect(self.display)
		
		icon = QIcon.fromTheme('edit-select-all')
		select_all_action = QAction(icon, 'Select All', self)
		select_all_action.setShortcut(QKeySequence.SelectAll)
		select_all_action.setStatusTip('Select All')
		select_all_action.triggered.connect(self.select_all)
		
		menubar = self.menuBar()
		
		fileMenu = menubar.addMenu('&File')
		fileMenu.addAction(open_action)
		fileMenu.addAction(import_action)
		fileMenu.addAction(save_action)
		fileMenu.addAction(saveas_action)
		fileMenu.addAction(exit_action)
		
		toolsMenu = menubar.addMenu('&Edit')
		toolsMenu.addAction(select_all_action)
		
		editMenu = menubar.addMenu('&Tools')
		editMenu.addAction(display_action)
		
		# toolbars
		icon = QIcon.fromTheme('snap-orthogonal')
		move_restrictions_action = QAction(icon, 'Move restrictions', self,
		                                   checkable=True)
		move_restrictions_action.setShortcut('Ctrl+R')
		move_restrictions_action.setStatusTip('Restrict movements')
		move_restrictions_action.toggled.connect(self.set_move_restrictions)
		
		# name must be unique (it is used internally by saveState()
		name = "Move restrictions"
		move_restrictions_toolbar = QToolBar(name, parent=self)
		move_restrictions_toolbar.setObjectName(name)
		move_restrictions_toolbar.addAction(move_restrictions_action)
		
		self.addToolBar(move_restrictions_toolbar)
		
		self.error_dialog = QErrorMessage(parent=self)
		self.error_dialog.setModal(True)
		# to use it, remember to .exec() it :
		#self.error_dialog.showMessage(message_str)
		#self.error_dialog.exec()
		
		# get windows settings
		# this must be at the end, because toolbar names must have been defined
		self.read_settings()
		
	def start(self):
		"""Start GUI."""
		
		if app_created_here:
			sys.exit(app.exec_())
	
	def exit(self):
		"""Clean exit."""
		
		self.close()
		
	def closeEvent(self, event):
		"""Overload QMainWindow."""
		
		self.write_settings()
		QMainWindow.closeEvent(self, event)
		# we could call a dialog, and on cancel, call event.ignore()
	
	def display(self):
		"""Dump the scene configuration to :obj:`sys.stdout`."""
		self.dump(stream=sys.stdout)
	
	def dump(self, stream=None):
		"""Dump the scene configuration to stream.
		
		Args:
			stream (file object, optional): by default, use :obj:`sys.stdout`
		"""
		if stream is None:
			# do not put stream=sys.stdout in the function header
			# this would yields
			# "AttributeError: 'bool' object has no attribute 'write'"
			stream = sys.stdout
		config = {'Scene': self.scene.config}
		yaml.dump(config, stream=stream)
	
	@pyqtSlot()
	def import_slot(self):
		"""Fire up a file dialog, and append the file content to the scene."""
		
		self.load_with_dialog(reset_scene=False)
	
	def import_file(self, filename):
		"""Import regions and sources from file.
		
		Previous elements in the scene are left untouched.
		"""
		with open(filename, 'r') as f:
			config = yaml.safe_load(stream=f)
			if 'Scene' in config:
				self.scene.add(config['Scene'])
			else:
				self.scene.add(config)
	
	@pyqtSlot()
	def open(self):
		"""Fire up a file dialog, empty scene, and load the file content."""
		
		self.load_with_dialog(reset_scene=True)
	
	def load_file(self, filename, reset_scene=True):
		"""Import regions and sources from file.
		
		Args:
			filename (str): path or name of the file to load from
			reset_scene (bool): If True, the scene is emptied before loading
		"""
		config_backup = self.scene.config
		try:
			if reset_scene:
				self.scene.clear()
			self.import_file(filename)
			logger.info("import from {} succeeded".format(filename))
			success = True
			message_str = ""
		except Exception as e:
			# rollback
			message_str = ("import from {} failed\n"
			               "  here is the exception:\n"
			               "  {}\n"
			               "  =>rolling back").format(filename, e)
			logger.info(message_str)
			self.scene.config = config_backup
			success = False
		return success, message_str
	
	def load_with_dialog(self, reset_scene=True):
		"""Open a file dialog and load the file content into the scene.
		
		If the dialog is cancelled, the scene is left untouched.
		
		Args:
			reset_scene (bool): see :meth:`load_file`.
		"""
		if reset_scene:
			caption = "Select file to open"
		else:
			caption = "Select file to import from"
		
		# discard the filter used
		filename, _ = QFileDialog.getOpenFileName(
		    parent=self,
		    caption=caption,
		    directory="./",
		    filter="GeOptics files (*.geoptics);; All files (*)"
		)
		# upon cancel filename is empty and this step is skipped
		if filename:
			success, message_str = self.load_file(filename, reset_scene)
			if not success:
				# tried with self.error_dialog, but
				# the checkbox was not honored (kept showing up);
				# giving up...
				#self.error_dialog.showMessage(message_str)
				#self.error_dialog.exec()
				# a simple QMessageBox is enough
				message_box = QMessageBox()
				message_box.critical(self, "Error", message_str)
				# try again
				self.load_with_dialog(reset_scene)
	
	def print_(self, *args):
		"""Print immediately to stderr.
		
		Same as ``print(*args)``,
		but do not block until exit.
		"""
		str = "".join(["{}".format(arg) for arg in args])
		qDebug(str)
	
	@pyqtSlot()
	def save(self):
		"""Save current session to the current file (overwrite)."""
		
		self.saveas(self.current_filename)
	
	# need the @pyqtSlot() decorator,
	# otherwise this slot would be called
	# with an argument, "checked", which is a boolean
	# filename would get this boolean value, instead of the default value
	@pyqtSlot()
	def saveas(self, filename=None):
		"""Save session to file.
		
		Args:
			filename (str):
				the path or name of the file to save to.
				If filename is `None`, then open a file dialog.
		"""
		if filename is None:
			# discard the filter used
			filename, _ = QFileDialog.getSaveFileName(
			    parent=self,
			    caption="Saving as...",
			    directory="./",
			    filter="GeOptics files (*.geoptics);; All files (*)"
			)
		if filename:
			with open(filename, 'w') as f:
				self.dump(stream=f)
				logger.info("saved to {}".format(filename))
				self.current_filename = filename
		else:
			logger.warning('Filename is "{}", save cancelled'.format(filename))
	
	@pyqtSlot(bool)
	def set_move_restrictions(self, state):
		"""Set move restrictions on/off.
		
		Args:
			state (bool):
				if True, movements are constrained to be horizontal or vertical.
		"""
		
		#print "move restrictions: ", state
		self.scene.g.move_restrictions_on = state
		
	def write_settings(self):
		"""Store application settings."""
		
		settings = QSettings()
		settings.beginGroup("MainWindow")
		settings.setValue("size", self.size())
		settings.setValue("pos", self.pos())
		settings.setValue("MainwindowState", self.saveState())
		settings.endGroup()
		
	def read_settings(self):
		"""Read application settings."""
		
		# remember we use sip.setapi('QVariant', 2)
		# in gui.qt.__init__.py (more info there)
		# hence we _must_ give the "type=" keyword arguments to value()
		settings = QSettings()
		settings.beginGroup("MainWindow")
		self.resize(settings.value("size", QSize(400, 400), type=QSize))
		self.move(settings.value("pos", QPoint(10, 10), type=QPoint))
		self.restoreState(settings.value("MainwindowState"))
		settings.endGroup()
	
	def select_all(self):
		"""Select all items in the scene."""
		
		self.scene.g.signal_set_all_selected.emit(True)
