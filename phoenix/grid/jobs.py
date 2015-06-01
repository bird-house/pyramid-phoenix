from phoenix.grid import MyGrid

class JobsGrid(MyGrid):
    def __init__(self, request, *args, **kwargs):
        super(JobsGrid, self).__init__(request, *args, **kwargs)
        self.column_formats['status'] = self.status_td
        self.column_formats['job'] = self.uuid_td
        self.column_formats['process'] = self.process_td
        self.column_formats['service'] = self.service_td
        self.column_formats['duration'] = self.duration_td
        self.column_formats['finished'] = self.finished_td
        self.column_formats['progress'] = self.progress_td
        self.column_formats[''] = self.action_td
        self.exclude_ordering = self.columns

    def status_td(self, col_num, i, item):
        return self.render_status_td(item)

    def uuid_td(self, col_num, i, item):
        return self.render_button_td(
            url=self.request.route_path('monitor_details', tab='log', jobid=item.get('identifier')),
            title=item.get('identifier'))
    
    def process_td(self, col_num, i, item):
        return self.render_label_td(item.get('title'))

    def service_td(self, col_num, i, item):
        return self.render_label_td(item.get('service'))

    def duration_td(self, col_num, i, item):
        return self.render_td(renderer="duration_td",
                              duration=item.get('duration', "???"),
                              identifier=item.get('identifier'))
        
    def finished_td(self, col_num, i, item):
        return self.render_time_ago_td(item.get('finished'))

    def progress_td(self, col_num, i, item):
        return self.render_progress_td(identifier=item.get('identifier'), progress = item.get('progress', 0))
        
    def action_td(self, col_num, i, item):
        buttongroup = []
        buttongroup.append( ("remove", item.get('identifier'), "glyphicon glyphicon-trash text-danger", "Remove Job", 
                             self.request.route_path('remove_job', jobid=item.get('identifier')), False) )
        return self.render_action_td(buttongroup)
