from zope.interface import Interface, Attribute

class ILinksList(Interface):
    """ Interface for LinksList"""
    pass

class ILocalChannel(Interface):
    """ Interface for LocalChannel"""
    pass

class IRemoteChannel(Interface):
    """ Interface for RemoteChannel"""
    pass

class IRemoteChannelFacade(Interface):
    """ Interface for RemoteChannelFacade"""
    pass

class IScriptChannel(Interface):
    """ Interface for ScriptChannel"""
    pass

class IChannelAggregator(Interface):
    """ Interface for ChannelAggregator"""
    pass

class IDynamicPropertiesItem(Interface):
    """ Interface for DynamicPropertiesItem"""
    pass

class ICSVImportExtraColumns(Interface):
    """
    When bulk-uploading CSV data, columns are mapped to schema
    properties. Some columns may not map to anything, and they would
    be ignored. For each row, if we can find an adapter that provides
    this interface, it will receive the additional CSV data.
    """

    def handle_columns(extra_properties):
        """ Handle extra CSV data columns """
