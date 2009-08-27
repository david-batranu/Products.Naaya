# The contents of this file are subject to the Mozilla Public
# License Version 1.1 (the "License"); you may not use this file
# except in compliance with the License. You may obtain a copy of
# the License at http://www.mozilla.org/MPL/
#
# Software distributed under the License is distributed on an "AS
# IS" basis, WITHOUT WARRANTY OF ANY KIND, either express or
# implied. See the License for the specific language governing
# rights and limitations under the License.
#
# The Initial Owner of the Original Code is European Environment
# Agency (EEA). Portions created by Eau de Web are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# David Batranu, Eau de Web


#Python imports

#Zope imports
from DateTime import DateTime
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens
from OFS.Folder import Folder

#Naaya imports
from Products.naayaUpdater.update_scripts import UpdateScript, PRIORITY
from Products.Naaya.NyFolder import NyFolder
from Products.NaayaBase.NyContentType import NyContentType

class MigrateCatalog(UpdateScript):
    """ Migrate catalog to Zope 2.10 """
    id = 'migrate_catalog2z210'
    title = 'Migrate catalogs to Zope 2.10'
    #meta_type = 'Naaya Update Script'
    creation_date = DateTime('Aug 27, 2009')
    authors = ['David Batranu']
    #priority = PRIORITY['LOW']
    description = ('Updates catalogs to Zope 2.10.'
                   'Replaces textindexng2 with textindexng3.'
                   'WARNING: This update will clear the portal catalog and recatalog only NyContentTypes')
    #dependencies = []
    #categories = []

    security = ClassSecurityInfo()


    def update_textindexng(self, catalog):
        indexes = [(index_id, catalog.Indexes._getOb(index_id)) for index_id in catalog.Indexes.objectIds()]
        for idx_id, idx_ob in indexes:
            if idx_ob.id != 'broken':
                continue
            else:
                catalog.Indexes.manage_delIndex([idx_id])
                catalog.manage_addProduct['TextIndexNG3'].manage_addTextIndexNG3(
                    id=idx_id,
                    extra={'default_encoding': 'utf-8',
                           'splitter_casefolding': True,
                    })

    def recatalog_portal_content(self, portal):
        self.walk_folders(folder=portal)
        portal.getCatalogTool().refreshCatalog(clear=1)

    def walk_folders(self, folder):
        for ob in folder.objectValues():
            if not isinstance(ob, (NyContentType, NyFolder)):
                continue
            portal = folder.getSite()
            portal.catalogNyObject(ob)
            if isinstance(ob, NyFolder):
                self.walk_folders(ob)

    security.declarePrivate('_update')
    def _update(self, portal):
        catalogs = portal.ZopeFind(portal, obj_metatypes=['ZCatalog', 'Naaya Catalog Tool'], search_sub=1)
        for catalog in [x[1] for x in catalogs]:
            self.update_textindexng(catalog)
            catalog.manage_catalogClear()
            catalog.manage_convertIndexes()
            self.log.debug('Cleared and converted catalog %s' % catalog.absolute_url(1))
        self.recatalog_portal_content(portal)
        self.log.debug('Rebuilt portal catalog')
        return True


