<div>
  % if labels:
  %   for label in labels:
  %     if label == 'public':
  <a href="/monitor?access=public" class="label label-warning">${label}</a>
  %     elif label == 'bug':
  <a href="/monitor?tag=${label}" class="label label-danger">${label}</a>
  %     elif label == 'fav':
  <a href="/monitor?tag=${label}" class="label label-success">${label}</a>
  %     elif label in ['workflow', 'single']:
  <a href="/monitor?tag=${label}" class="label label-default">${label}</a>
  %     else:
  <a href="/monitor?tag=${label}" class="label label-info">${label}</a>
  %     endif
  %   endfor
  % else:
  <span class="label label-default">No Labels</span>
  % endif            
  <br>
    <a class="labels" data-value="${job_id}" href="#">
      edit labels
    </a>
 </div>
