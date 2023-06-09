# -*- coding: utf-8 -*-
"""
/***************************************************************************
 addgeelayers
                                 A QGIS plugin
 Add NDVI, PCA, false color layers to QGIS using GEE
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2021-07-06
        copyright            : (C) 2021 by William Martinez
        email                : willimarti2008@gmail.com
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""

from .addgeelayers import addgeelayers

debug = True
# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load addgeelayers class from file addgeelayers.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    return addgeelayers(iface)
