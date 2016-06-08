<%
  clean_labels = [l.strip() for l in labels.split(',')]
%>
<div>
  % for label in clean_labels:
  %     if label == 'public':
  <a href="#" class="label label-warning">${label}</a>
  %     else:
  <a href="#" class="label label-info">${label}</a>
  %     endif
  % endfor
              
  <br>
    <a class="labels" data-value="${job_id}" href="#">
      edit labels
    </a>
 </div>
