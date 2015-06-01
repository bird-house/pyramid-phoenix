<% 
   if status == 'ProcessSucceeded':
     icon_class="glyphicon glyphicon-ok-sign text-success"
   elif status == 'ProcessFailed':
     icon_class="glyphicon glyphicon-remove-sign text-danger"
   elif status == 'ProcessPaused':
     icon_class="glyphicon glyphicon-paused text-muted"
   elif status == 'ProcessStarted' or status == 'ProcessAccepted':
     icon_class="glyphicon glyphicon-cog text-muted"
   else:
     icon_class="glyphicon glyphicon-question-sign text-danger"
%>
<div>
  <i class="${icon_class}" data-toggle="tooltip" title="${status}"
     id="status-${identifier}"></i>
</div>
