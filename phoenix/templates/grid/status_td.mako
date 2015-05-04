<div>
  % if status == 'ProcessSucceeded':
  <i class="glyphicon glyphicon-ok-sign text-success" data-toggle="tooltip" title="${status}"></i>
  % elif status == 'ProcessFailed':
  <i class="glyphicon glyphicon-remove-sign text-danger" data-toggle="tooltip" title="${status}"></i>
  % elif status == 'ProcessPaused':
  <i class="glyphicon glyphicon-paused text-muted" data-toggle="tooltip" title="${status}"></i>
  % elif status == 'ProcessStarted' or status == 'ProcessAccepted':
  <i class="glyphicon glyphicon-cog text-muted" data-toggle="tooltip" title="${status}"></i>
  % else:
  <i class="glyphicon glyphicon-question-sign text-danger" data-toggle="tooltip" title="${status}"></i>
  % endif
</div>
