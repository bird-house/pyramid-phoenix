<% 
   if status == 'ProcessSucceeded':
     icon_class="fa fa-check-circle text-success"
   elif status == 'ProcessFailed':
     icon_class="fa fa-times-circle text-danger"
   elif status == 'ProcessPaused':
     icon_class="fa fa-pause text-muted"
   elif status == 'ProcessStarted' or status == 'ProcessAccepted':
     icon_class="fa fa-gear fa-spin text-muted"
   else:
     icon_class="fa fa-fw fa-clock-o pulse text-muted"
%>
<div>
  <i class="${icon_class}" data-toggle="tooltip" title="${status}"
     id="status-${identifier}"></i>
</div>
