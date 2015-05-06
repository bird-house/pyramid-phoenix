from phoenix.grid import MyGrid

class ProcessOutputsGrid(MyGrid):
    def __init__(self, request, *args, **kwargs):
        super(ProcessOutputsGrid, self).__init__(request, *args, **kwargs)
        self.column_formats['output'] = self.output_td
        self.column_formats['value'] = self.value_td
        #self.column_formats['preview'] = self.preview_td
        self.column_formats[''] = self.action_td
        self.exclude_ordering = self.columns

        from string import Template
        url_templ = Template("${url}/godiva2/godiva2.html?server=${url}/wms/test")
        thredds_url = request.registry.settings.get('thredds.url')
        self.wms_url = url_templ.substitute({'url': thredds_url})

    def output_td(self, col_num, i, item):
        return self.render_title_td(
            title=item.get('title'), 
            abstract=item.get('abstract', ""))

    def value_td(self, col_num, i, item):
        return self.render_td(renderer="value_td",
                data=item.get('data', []),
                format=item.get('mime_type'),
                source=item.get('reference'))

    def preview_td(self, col_num, i, item):
        return self.render_preview_td(format=item.get('mime_type'), source=item.get('reference'))

    def action_td(self, col_num, i, item):
        # TODO: dirty hack ...
        buttongroup = []
        if item.get('reference') is not None:
            # TODO: dirty hack for show on map
            wms_reference = self.wms_url + item.get('reference').split('wpsoutputs')[1]
            buttongroup.append( ("publish", item.get('identifier'), "glyphicon glyphicon-share", "Publish", "#", False) )
            buttongroup.append( ("view", item.get('identifier'), "glyphicon glyphicon-eye-open", "View", 
                                 item.get('reference', "#"), True) )
            buttongroup.append( ("mapit", item.get('identifier'), "glyphicon glyphicon-globe", "Show on Map",
                                 wms_reference, True) )
            buttongroup.append( ("upload", item.get('identifier'), "glyphicon glyphicon-upload", "Upload",
                                 "#", False) )
        return self.render_action_td(buttongroup)
