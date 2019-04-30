# -*- coding: utf-8 -*-
"""
/***************************************************************************
 SIGRDAP
                                 A QGIS plugin
 Sistema de Información Geográfica que permite realizar operaciones relacionadas con una Red de Distribución de Agua Potable
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2018-05-11
        copyright            : (C) 2018 by Jair Nájera / HTech
        email                : riaj.16.erre@gmail.com
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


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load SIGRDAP class from file SIGRDAP.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .sigrdap import SIGRDAP
    return SIGRDAP(iface)
