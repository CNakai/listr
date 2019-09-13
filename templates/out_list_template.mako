<%page args="requests"/>
<!DOCTYPE html>

<html lang="en">
  <head>
    <meta charset="utf-8"/>
    <title>Listr</title>
    <style>
     <%include file="out_list_style.css"/>
    </style>

    <%include file="out_list_scripts.mako" args="requests=requests"/>
  </head>

  <body>
    <div id="js-button-frame"></div>
    <div id="pending-requests">
      <table>
        <thead><tr>
          <th>Name:</th> <th>Colors:</th> <th>Rarity:</th> <th>Set:</th>
          <th>Qty:</th>
        </tr></thead>
        <tbody class="js-render-area"
               data-render-type="srcn"
               data-columns="name colors rarity printing quantityUnfulfilled"
               data-sort-order="name colors rarity3 printing"></tbody>
      </table>
      <table>
        <thead><tr>
          <th>Name:</th> <th>Colors:</th> <th>Rarity:</th> <th>Qty:</th>
        </tr></thead>
        <tbody class="js-render-area"
               data-render-type="cn"
               data-columns="name colors rarity quantityUnfulfilled"
               data-sort-order="name colors rarity2"></tbody>
      </table>
      <table>
        <thead><tr>
          <th>Name:</th> <th>Colors:</th> <th>Rarity:</th> <th>Qty:</th>
        </tr></thead>
        <tbody class="js-render-area"
               data-render-type="compact"
               data-columns="name colors rarity quantityUnfulfilled"
               data-sort-order="name colors rarity2"></tbody>
      </table>
    </div>

    <div id="processed-requests">
      <table>
        <thead><tr><th>Name:</th> <th>Set:</th> <th>Qty:</th></tr></thead>
        <tbody class="js-render-area"
               data-render-type="fulfilled"
               data-columns="name printing quantityFulfilled"
               data-sort-order="printing name"></tbody>
      </table>
      <table>
        <thead><tr><th>Name:</th> <th>Set:</th></tr></thead>
        <tbody class="js-render-area"
               data-render-type="denied"
               data-columns="name printing"
               data-sort-order="printing name"></tbody>
      </table>
    </div>
  </body>
</html>
