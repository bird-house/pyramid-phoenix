<% 
   if status == 'ProcessSucceeded':
     icon_class="fa fa-check-circle text-success"
   elif status == 'ProcessFailed':
     icon_class="fa fa-times-circle text-danger"
   elif status == 'ProcessPaused':
     icon_class="fa fa-pause text-muted"
   elif status == 'ProcessStarted':
     icon_class="fa fa-gear fa-spin text-muted"
   else:
     icon_class="fa fa-fw fa-clock-o pulse text-muted"
%>
<div>
  <i class="${icon_class}" data-toggle="tooltip" title="${status}" id="status-${job_id}"> </i>
  % if status in ['ProcessStarted', 'ProcessPaused', 'ProcessFailed']:
  <div class="progress">
    <div class="progress-bar progress-bar-info" role="progressbar" aria-valuenow="${progress}" aria-valuemin="0" aria-valuemax="100" style="width: ${progress}%;" id="progress-${job_id}">
      <span>${progress}%</span>
    </div>
  </div>
  % endif
 
</div>
