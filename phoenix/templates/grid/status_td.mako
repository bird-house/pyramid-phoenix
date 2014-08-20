<div>
  <div>
    <span class="${span_class}" id="status-${item.get('identifier')}">${item.get('status')}</span>
    <div id="message-${item.get('identifier')}">${item.get('status_message')}</div>
  </div>
  <div>
    <a class="label label-warning" href="${item.get('status_location')}" data-format="XML">XML</a>
  </div>
</div>
