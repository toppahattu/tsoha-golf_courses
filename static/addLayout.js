function initializeForm() {
    let inputs = document.getElementsByName('layoutname')
    for (const input of inputs) {
        input.addEventListener('input', addNewLayout)
    }
}

function addNewLayout() {
    let form = document.forms.courseform
    let inputs = document.getElementsByName('layoutname')
    let empty = false

    for (let i=inputs.length - 1; i > -1; i--) {
        let input = inputs[i]
        if (input.value.trim() === '' && empty) {
            let label = inputs[i].parentNode
            let div = label.parentNode
            let container = div.parentNode
            container.remove()
        }
        if (input.value.trim() === '') {
            empty = true
        }
    }
    if (!empty) {
        let container = document.createElement('div')
        container.className = 'layoutcontainer'
        let divName = document.createElement('div')
        divName.className = 'form-group'
        let divPar = document.createElement('div')
        divPar.className = 'form-group'
        let divHoles = document.createElement('div')
        divHoles.className = 'form-group'

        let nameLabel = document.createElement('label')
        nameLabel.textContent = 'Kentän nimi: '
        let nameInput = document.createElement('input')
        nameInput.setAttribute('type', 'text')
        nameInput.className = 'form-control'
        nameInput.setAttribute('name', 'layoutname')
        nameInput.addEventListener('input', addNewLayout)

        let parLabel = document.createElement('label')
        parLabel.textContent = 'Kentän par: '
        let parInput = document.createElement('input')
        parInput.setAttribute('type', 'text')
        parInput.className = 'form-control'
        parInput.setAttribute('name', 'layoutpar')

        let holesLabel = document.createElement('label')
        holesLabel.textContent = 'Kentän reikien lukumäärä: '
        let holesInput = document.createElement('input')
        holesInput.setAttribute('type', 'text')
        holesInput.className = 'form-control'
        holesInput.setAttribute('name', 'layoutholes')

        container.appendChild(divName).appendChild(nameLabel).appendChild(nameInput)
        container.appendChild(divPar).appendChild(parLabel).appendChild(parInput)
        container.appendChild(divHoles).appendChild(holesLabel).appendChild(holesInput)
        form.elements.layouts.appendChild(container)
    }
}

window.addEventListener('load', initializeForm)