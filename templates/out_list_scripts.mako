<%text>
    <script type="text/javascript">
     function setUpListeners() {
         for (let cb of document.querySelectorAll('input')) {
             cb.addEventListener('change', checkboxListener)
         }
     }

     function checkboxListener() {
         console.log(this)
         const card_name = this.parentNode.dataset['name']
         const set = this.parentNode.dataset['set']
         const all_occurrences = document.querySelectorAll(`[data-name="${card_name}"]`)

         for (const occurrence of all_occurrences) {
             if (this.checked && set !== occurrence.dataset['set']) {
                 occurrence.style.display = 'none'
             } else {
                 occurrence.style.display = 'block'
             }
         }
     }

     setUpListeners()
    </script>
</%text>
