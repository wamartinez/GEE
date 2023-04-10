# -*- coding: utf-8 -*-
"""
/***************************************************************************
 addgeelayers
                                 A QGIS plugin
 Add NDVI, TCT, NBR, Composites layers to QGIS using GEE
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2021-07-06
        git sha              : $Format:%H$
        copyright            : (C) 2021 by William Martinez
        email                : willimarti2008@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QMessageBox, QDateEdit,QVBoxLayout
from qgis.core import QgsProject ,QgsMapLayer

# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .addgeelayers_dialog import addgeelayersDialog
import os.path
import numpy as np


class addgeelayers:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'addgeelayers_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&addgeelayers')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None

        #date
        #self.startDateEdit = QDateEdit()
        #self.startDateEdit.setCalendarPopup(True)

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('addgeelayers', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/addgeelayers/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Add GEE layers'),
            callback=self.run,
            parent=self.iface.mainWindow())

        # will be set False in run()
        self.first_start = True


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&addgeelayers'),
                action)
            self.iface.removeToolBarIcon(action)


    def run(self):
        import ee
        ee.Initialize()
        from .gee_functions import map_gee_layers

        """Run method that performs all the real work"""
        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        if self.first_start == True:
            self.first_start = False
            self.dlg = addgeelayersDialog()
            self.dlg.RB_S2.toggled.connect(lambda:self.btnstate_S2(self.dlg.RB_S2))
            self.dlg.RB_L8.toggled.connect(lambda:self.btnstate_L8(self.dlg.RB_L8))
            self.dlg.RB_L5.toggled.connect(lambda:self.btnstate_L5(self.dlg.RB_L5)) 
            self.dlg.RB_L7.toggled.connect(lambda:self.btnstate_L7(self.dlg.RB_L7))
            #saving data
            self.dlg.save_data.toggled.connect(lambda:self.btnstate_sd(self.dlg.save_data))
            #self.dlg.cmbComputation.currentTextChanged.connect(self.cmbComputation_changed)

        # Fetch the currently loaded layers
        layers = QgsProject.instance().layerTreeRoot().children()
        name_layers = []
        for i in layers:
            if i.layer().type() == QgsMapLayer.VectorLayer and i.layer().crs().authid() == u'EPSG:4326':
                name_layers.append(i.name())

        # Clear the contents of the comboBox from previous runs
        self.dlg.CBselectLayer.clear()
        # Populate the comboBox with names of all the loaded layers
        # self.dlg.CBselectLayer.addItems([layer.name() for layer in layers])
        self.dlg.CBselectLayer.addItems(name_layers)

        #some buttons checked
        #self.dlg.RB_S2.setChecked(True)
        # show the dialog
        self.dlg.show()

        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            if self.dlg.RB_S2.isChecked() == True:
                sensor = "S2"
            elif self.dlg.RB_L5.isChecked() == True:
                sensor = "L5"
            elif self.dlg.RB_L7.isChecked() == True:
                sensor = "L7"
            elif self.dlg.RB_L8.isChecked() == True:
                sensor = "L8"

            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            if not name_layers:
                QMessageBox.information(self.dlg,"Message","Layer must be vector in WGS84")
            else:
                #get values from this form
                valStart = self.dlg.startDateEdit.date()
                valEnd = self.dlg.endDateEdit.date()
                if valStart.daysTo(valEnd) <= 0:
                    QMessageBox.information(self.dlg,"Message","End date must be grater than the start date")
                else:
                    computation = self.dlg.cmbComputation.currentText()
                    state_ndvi = self.dlg.CheckBNDVI.checkState()
                    state_nbr = self.dlg.CheckBNBR.checkState()
                    state_tct = self.dlg.CheckBTCT.checkState()
                    #Composition
                    list_bands_composition = []
                    list_bands_composition.append(self.dlg.CBoxBand1.currentText())
                    list_bands_composition.append(self.dlg.CBoxBand2.currentText())
                    list_bands_composition.append(self.dlg.CBoxBand3.currentText())
                    #min max gamma
                    gamma = self.dlg.gamma.value()
                    min_comp = self.dlg.min_comp.value()
                    max_comp = self.dlg.max_comp.value()
                    
                    #Saving data
                    if self.dlg.save_data.isChecked() == True:
                        folder = self.dlg.folder.text()
                        if folder == "":
                            QMessageBox.information(self.dlg,"Message","Define a name of the folder in Google Drive")
                            sdata_d = {'sdata': False, 'folder': np.nan}
                        else:
                            sdata_d = {'sdata': True, 'folder': folder}
                    else:
                        sdata_d = {'sdata': False, 'folder': np.nan}
                    
                    #get coordinates
                    layer_name = self.dlg.CBselectLayer.currentText()
                    extension = [ly.layer().extent() for ly in layers if layer_name == ly.name()]
                    #pass
                    Minx = extension[0].xMinimum()    
                    Maxx = extension[0].xMaximum()    
                    Miny = extension[0].yMinimum()   
                    Maxy = extension[0].yMaximum()    
                    list_extent = [[Minx,Miny],[Maxx,Miny],[Maxx,Maxy],[Minx,Maxy],[Minx,Miny]]
                    map_gee_layers(self,list_extent,valStart,valEnd,computation,state_ndvi,state_nbr,state_tct,list_bands_composition,sensor,min_comp, max_comp, gamma,sdata_d)
                    print("Done")
        

    def btnstate_S2(self,bt):
        if bt.isChecked() == True:
            self.dlg.textEditSensor.setText(" Sentinel 2 Level-2A: \n 2017-03-28 - 2023-02-19 ")
            #Populate Combobox of compositions
            #S1
            self.dlg.CBoxBand1.clear()
            self.dlg.CBoxBand2.clear()
            self.dlg.CBoxBand3.clear()
            list_S2 = ["B1","B2","B3","B4","B5","B6","B7","B8","8A","B9","B11","B12"]
            self.dlg.CBoxBand1.addItems(list_S2)
            self.dlg.CBoxBand2.addItems(list_S2)    
            self.dlg.CBoxBand3.addItems(list_S2)
            #values of min, max and gamma
            self.dlg.gamma.setValue(1)
            self.dlg.min_comp.setValue(250)
            self.dlg.max_comp.setValue(3800)         

    def btnstate_L8(self,bt):
        if bt.isChecked() == True:
            self.dlg.textEditSensor.setText(" Landsat 8 TOA: \n 2013-04-11 - 2023-02-14")
            #L8
            self.dlg.CBoxBand1.clear()
            self.dlg.CBoxBand2.clear()
            self.dlg.CBoxBand3.clear()
            list_L8 = ["B2","B3","B4","B5","B6","B7","B8","B11","B12"]
            self.dlg.CBoxBand1.addItems(list_L8)
            self.dlg.CBoxBand2.addItems(list_L8)    
            self.dlg.CBoxBand3.addItems(list_L8)
            #values of min, max and gamma
            self.dlg.gamma.setValue(1.6)
            self.dlg.min_comp.setValue(250)
            self.dlg.max_comp.setValue(30000)


    def btnstate_L5(self,bt):
        if bt.isChecked() == True:
            self.dlg.textEditSensor.setText(" Landsat 5 ETM: \n 1984-01-01 - 2012-05-05")
            #L5
            self.dlg.CBoxBand1.clear()
            self.dlg.CBoxBand2.clear()
            self.dlg.CBoxBand3.clear()
            list_L5 = ["B1","B2","B3","B4","B5","B6","B7","B8"]
            self.dlg.CBoxBand1.addItems(list_L5)
            self.dlg.CBoxBand2.addItems(list_L5)    
            self.dlg.CBoxBand3.addItems(list_L5)
            #values of min, max and gamma
            self.dlg.gamma.setValue(1.6)
            self.dlg.min_comp.setValue(250)
            self.dlg.max_comp.setValue(3000)

    
    def btnstate_L7(self,bt):
        if bt.isChecked() == True:
            self.dlg.textEditSensor.setText(" Landsat 7 ETM+: \n 1999-01-01 - 2021-06-15")
            #L7
            self.dlg.CBoxBand1.clear()
            self.dlg.CBoxBand2.clear()
            self.dlg.CBoxBand3.clear()
            list_L7 = ["B1","B2","B3","B4","B5","B6","B7","B8"]
            self.dlg.CBoxBand1.addItems(list_L7)
            self.dlg.CBoxBand2.addItems(list_L7)    
            self.dlg.CBoxBand3.addItems(list_L7)
            #values of min, max and gamma
            self.dlg.gamma.setValue(1.6)
            self.dlg.min_comp.setValue(250)
            self.dlg.max_comp.setValue(30000)

    def btnstate_sd(self,bt):
        if bt.isChecked() == True:
            self.dlg.folder.setDisabled(False)
        else:
            self.dlg.folder.setDisabled(True)








