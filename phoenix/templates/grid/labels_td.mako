<div>
  % for label in labels.split(','):
  %     if label.strip() == 'main':
  <a href="#" class="label label-warning">${label.strip()}</a>
  %     else:
  <a href="#" class="label label-info">${label.strip()}</a>
  %     endif
  % endfor
              
  <br>
    <a class="labels" data-value="${job_id}" href="#">
      edit labels
    </a>
 </div>
