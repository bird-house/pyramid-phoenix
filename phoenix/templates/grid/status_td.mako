<div>
  % if item['status'] == 'ProcessSucceeded':
  <i class="glyphicon glyphicon-ok-sign text-success"></i>
  % elif item['status'] == 'ProcessFailed':
  <i class="glyphicon glyphicon-remove-sign text-danger"></i>
  % elif item['status'] == 'ProcessPaused':
  <i class="glyphicon glyphicon-paused text-muted"></i>
  % elif item['status'] == 'ProcessStarted' or item['status'] == 'ProcessAccepted':
  <i class="glyphicon glyphicon-cog text-muted"></i>
  % else:
  <i class="glyphicon glyphicon-question-sign text-danger"></i>
  % endif
</div>
