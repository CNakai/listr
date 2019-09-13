## -*- coding: utf-8 -*-
<%page args="requests"/>
<%! import json %>
<script type="text/javascript">

 const requestsData = ${json.dumps(requests)};

 <%text>
 let renderMode = null

 function main () {
   const renderAreas = [...document.querySelectorAll('.js-render-area')]
   const cardRequests = [...requestsData.map((reqData) => {
     return new CardRequest(reqData, renderAreas)
   })]

   const renderModeButtons = setupRenderModeButtons(cardRequests)
   renderModeButtons[0].click()

   renderAreas.map(renderArea => sortRows(renderArea))
   cardRequests.map(cardReq => cardReq.updateRows())
 }


 function setupRenderModeButtons (cardRequests) {
   const buttonFrame = document.querySelector('#js-button-frame')

   const renderModeButtons = []
   for (renderType of ['split', 'srcn', 'cn', 'compact']) {
     const button = document.createElement('button')
     button.setAttribute('value', renderType)
     button.innerText = renderType

     button.addEventListener('click', () => {
       renderMode = button.value
       updateRequestTablesVisibility()
       cardRequests.map((cardReq) => cardReq.updateRows())
     })

     renderModeButtons.push(button)
     buttonFrame.append(button)
   }

   return renderModeButtons
 }


 function updateRequestTablesVisibility () {
   const hider = (el) => el.classList.add('hidden')
   const shower = (el) => el.classList.remove('hidden')
   const renderModeRules = {
     'split':   {'cn': shower, 'srcn': shower, 'compact': hider},
     'srcn':    {'cn': hider, 'srcn': shower, 'compact': hider},
     'cn':      {'cn': shower, 'srcn': hider, 'compact': hider},
     'compact': {'cn': hider, 'srcn': hider, 'compact': shower},
   }

   for (const [tableType, changer] of Object.entries(renderModeRules[renderMode])) {
     changer(document
       .querySelector(`[data-render-type="${tableType}"]`)
       .parentNode)
   }
 }


 function sortRows (tbody) {
   const comparators = {
     'name': (row1, row2) => {
       const value1 = getColValue(row1, 'name')
       const value2 = getColValue(row2, 'name')
       return value1.localeCompare(value2)
     },

     'colors': (row1, row2) => {
       const value1 = getColValue(row1, 'colors')
       const value2 = getColValue(row2, 'colors')

       if (value1 === value2) {return 0}
       else if (value1 === 'L') { return 1 }
       else if (value2 === 'L') { return -1 }
       else if (value1 === 'C') { return 1 }
       else if (value2 === 'C') { return -1 }
       else if (value1.length === 1 && value2.length === 1) {
         const order = 'WUBRG'
         return order.indexOf(value1[0].toUpperCase()) -
                order.indexOf(value2[0].toUpperCase())
       }

       return value1.length - value2.length
     },

     'rarity2': (row1, row2) => {
       const orderValues = {'COMMON': 0, 'UNCOMMON': 0, 'RARE': 1, 'MYTHIC': 1}
       return orderValues[getColValue(row1, 'rarity').toUpperCase()] -
              orderValues[getColValue(row2, 'rarity').toUpperCase()]
     },

     'rarity3': (row1, row2) => {
       const orderValues = {'COMMON': 0, 'UNCOMMON': 1, 'RARE': 2, 'MYTHIC': 2}
       return orderValues[getColValue(row1, 'rarity').toUpperCase()] -
              orderValues[getColValue(row2, 'rarity').toUpperCase()]
     },

     'printing': (row1, row2) => {
       return getColValue(row1, 'printing')
         .localeCompare(getColValue(row2, 'printing'))
     }
   }

   for (const sortKey of tbody.dataset.sortOrder.split(' ')) {
     const rows = [...tbody.querySelectorAll('tr')]
     rows.sort(comparators[sortKey])
     rows.map(r => r.parentNode.appendChild(r))
   }
 }


 function getColValue (row, colName) {
   return row.querySelector(`[name="${colName}"]`).innerText
 }


 class CardRequest {
   static get count () {
     return CardRequest._count
   }

   static incCount () {
     return ++CardRequest._count
   }


   constructor (requestData, renderAreas) {
     this.id = CardRequest.count
     CardRequest.incCount()

     this.name = requestData['name']
     this.colors = requestData['colors']
     this.rarity = requestData['rarity']
     this.quantityRequested = requestData['quantity']
     this.deniedPrintings = []

     this.printingsToOrderings = new Map([['---', 'cn']].concat(
       [...Object.entries(requestData['printings'])]
     ))

     this.printingsToFoundCounts = new Map(
       [...this.printingsToOrderings.keys()].map(printing => [printing, 0])
     )
     this.printingsToFoundCounts.set('---', 0)


     for (const renderArea of renderAreas) {
       this._renderRows(renderArea)
     }

     this.rows = [...document
                  .querySelectorAll(`[data-request-object-id="${this.id}"]`)]
   }


   get quantityUnfulfilled () {
     return this.quantityRequested - this.quantityFulfilled
   }


   get quantityFulfilled () {
     return [...this.printingsToFoundCounts.values()]
       .reduce(((acc, val) => acc + val), 0)
   }


   get isMulticolor () {
     return this.colors.length > 1
   }


   get totalFound () {
     return [...this.printingsToFoundCounts.values()]
       .reduce(((acc, v) => acc + v), 0)
   }


   fulfill (printing, count) {
     const currentCount = this.printingsToFoundCounts.get(printing)
     this.printingsToFoundCounts.set(printing, currentCount + count)
     this.updateRows()
   }


   unfulfill (printing, count) {
     const currentCount = this.printingsToFoundCounts.get(printing)
     this.printingsToFoundCounts.set(printing, currentCount - count)
     this.updateRows()
   }


   deny (printing) {
     this.deniedPrintings.push(printing)
     this.updateRows()
   }


   undeny (printing) {
     this.deniedPrintings.splice(this.deniedPrintings.indexOf(printing), 1)
     this.updateRows()
   }


   updateRows () {
     for (const row of this.rows) {
       const fulfilledCol = row.querySelector('[name="quantityFulfilled"]')
       const unfulfilledCol = row.querySelector('[name="quantityUnfulfilled"]')
       const printing = row.querySelector('[name="printing"]')

       if (unfulfilledCol !== null) {
         unfulfilledCol.innerText = this.quantityUnfulfilled
         let printingVal = '---'
         if (printing !== null) {
           if (printing.nodeName === "SELECT") {
             printingVal = printing.options[printing.selectedIndex].value
             for (const option of printing.children) {
               if (this.deniedPrintings.includes(option.value) ||
                   this.printingsToFoundCounts.get(option.value) !== 0) {
                 option.classList.add('hidden')
               } else {
                 option.classList.remove('hidden')
               }
             }
           } else {
             printingVal = printing.innerText
           }
         }

         if (this.quantityUnfulfilled === 0 ||
             this.printingsToFoundCounts.get('---') !== 0 ||
             this.deniedPrintings.includes(printingVal) ||
             this.deniedPrintings.includes('---') ||
             this.deniedPrintings.length >=
               [...this.printingsToFoundCounts.keys()].length - 1 ||
             (renderMode === 'split' &&
              this.printingsToOrderings.get(printingVal) !==
                row.parentNode.dataset.renderType)) {
           row.classList.add('hidden')
         } else {
           row.classList.remove('hidden')
         }

       } else if (fulfilledCol !== null) {
         const printingVal = printing.innerText
         const fulfilledQuantity = this.printingsToFoundCounts.get(printingVal)
         fulfilledCol.innerText = fulfilledQuantity
         if (fulfilledQuantity === 0) {
           row.classList.add('hidden')
         } else {
           row.classList.remove('hidden')
         }
       } else {
         const printingVal = printing.innerText
         if (this.deniedPrintings.includes(printingVal)) {
           row.classList.remove('hidden')
         } else {
           row.classList.add('hidden')
         }
       }
     }
   }


   _renderRows (renderArea) {
     switch (renderArea.dataset.renderType) {
       case 'srcn': this._renderSRCNRows(renderArea); break
       case 'cn': this._renderCNRows(renderArea); break
       case 'compact': this._renderCompactRows(renderArea); break
       case 'fulfilled': this._renderFulfilledRows(renderArea); break
       case 'denied': this._renderDeniedRows(renderArea); break
     }
   }


   _renderSRCNRows (renderArea) {
     for (const [printing, ordering] of this.printingsToOrderings.entries()) {
       if (printing !== '---') {
         renderArea.appendChild(this._createRow(renderArea,
                                                {'printing': printing}))
       }
     }
   }


   _renderCNRows (renderArea) {
     renderArea.appendChild(this._createRow(renderArea, {}))
   }


   _renderCompactRows (renderArea) {
     renderArea.appendChild(this._createRow(renderArea, {}))
   }


   _renderFulfilledRows (renderArea) {
     for (const [printing, count] of this.printingsToFoundCounts.entries()) {
       renderArea.appendChild(this._createRow(renderArea,
                                              {
                                                'printing': printing,
                                                'count': count
                                              }))
     }
   }


   _renderDeniedRows (renderArea) {
     for (const printing of this.printingsToOrderings.keys()) {
       renderArea.appendChild(
         this._createRow(renderArea, {'printing': printing})
       )
     }
   }


   _createRow(renderArea, colParams) {
     const row = document.createElement('tr')
     row.setAttribute('data-request-object-id', this.id)
     row.classList.add(this.isMulticolor ? 'MC' : this.colors)

     for (const colName of renderArea.dataset.columns.split(' ')) {
       const col = document.createElement('td')
       col.setAttribute('name', colName)
       col.innerText = this[colName] !== undefined ?
                       this[colName] :
                       colParams[colName]
       row.appendChild(col)
     }

     const renderType = renderArea.dataset.renderType
     if (['srcn', 'cn'].includes(renderType)) {
       this._addFulfillDenyControls(row)
     } else if (renderType === 'compact') {
       this._addPrintingSelectionControls(row)
       this._addFulfillDenyControls(row)
     } else if (['fulfilled', 'denied'].includes(renderType)) {
       this._addUndoControls(row)
     }

     this._attachRowListeners(row, renderType)
     return row
   }


   _addFulfillDenyControls (row) {
     const fulfillDenyControls = document.createElement('td')

     const countInput = document.createElement('input')
     countInput.setAttribute('name', 'count')
     countInput.setAttribute('type', 'number')
     countInput.setAttribute('min', '1')
     countInput.setAttribute('max', this.quantityRequested)
     countInput.value = 1
     fulfillDenyControls.appendChild(countInput)

     const fulfillButton = document.createElement('button')
     fulfillButton.setAttribute('name', 'fulfill')
     fulfillButton.innerText = '👍'
     fulfillDenyControls.appendChild(fulfillButton)

     const denyButton = document.createElement('button')
     denyButton.setAttribute('name', 'deny')
     denyButton.innerText = '👎'
     fulfillDenyControls.appendChild(denyButton)

     row.appendChild(fulfillDenyControls)
   }


   _addPrintingSelectionControls (row) {
     const printingSelectionControls = document.createElement('td')
     const select = document.createElement('select')
     select.setAttribute('name', 'printing')
     printingSelectionControls.appendChild(select)

     for (const printing of [...this.printingsToOrderings.keys()]) {
       const option = document.createElement('option')
       option.value = printing
       option.innerText = printing
       select.appendChild(option)
     }

     row.appendChild(printingSelectionControls)
   }


   _addUndoControls (row) {
     const undoControls = document.createElement('td')
     const undoButton = document.createElement('button')
     undoButton.setAttribute('name', 'undo')
     undoButton.innerText = 'undo'
     undoControls.appendChild(undoButton)
     row.appendChild(undoControls)
   }

   _attachRowListeners (row, rowType) {
     const controller = this
     const count = row.querySelector('[name="count"]')
     const qtyFulfilledCol = row.querySelector('[name="quantityFulfilled"]')
     const printing = row.querySelector('[name="printing"]')

     const listeners = {
       'fulfill': function () {
         let printingVal = '---'
         if (printing !== null) {
           if (printing.nodeName === "SELECT") {
             printingVal = printing.options[printing.selectedIndex].value
             printing.selectedIndex = 0
           } else {
             printingVal = printing.innerText
           }
         }
         const countVal = parseInt(count.value, 10)
         count.value = 1
         controller.fulfill(printingVal, countVal)
       },

       'deny': function () {
         let printingVal = '---'
         if (printing !== null) {
           if (printing.nodeName === "SELECT") {
             printingVal = printing.options[printing.selectedIndex].value
             printing.selectedIndex = 0
           } else {
             printingVal = printing.innerText
           }
         }
         count.value = 1
         controller.deny(printingVal)
       },

       'undo': function () {
         if (qtyFulfilledCol !== null) { /* we're undoing a 'fulfill' */
           controller.unfulfill(printing.innerText, qtyFulfilledCol.innerText)
         } else { /* we're undoing a 'deny' */
           controller.undeny(printing)
         }
       }
     }

     for (const listenerType in listeners) {
       const button = row.querySelector(`[name="${listenerType}"]`)
       if (button !== null) {
         button.addEventListener('click', listeners[listenerType])
       }
     }
   }
 }

 CardRequest._count = 0


 window.addEventListener('DOMContentLoaded', (event) => main())
 </%text>
</script>
