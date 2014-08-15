<div class="btn-group">
  <a class="btn dropdown-toggle" data-toggle="dropdown" href="#">Action<span class="caret"></span></a>
  <ul class="dropdown-menu">
    <!-- dropdown menu links -->
    % for name,value,icon,title in buttongroup:
    <li><a class="${name}" data-value="${value}"><i class="${icon}"></i> ${title}</a></li>
    % endfor
  </ul>
</div>
