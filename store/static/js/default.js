let overlayId = document.getElementById('alerts');
let overlayCloseId = document.getElementById('close_alert');

let tooltips = document.querySelectorAll('span[role="tooltip"]');
let showAllTooltips = document.getElementById('show_all_help');
let tooltipList = {};
let forceShow = false;
let tooltipEvents = {
	'show':['mouseenter', 'focus', 'touchstart'],
	'hide':['mouseleave', 'blur', 'touchend']
};
let tooltipControls = {
	'show':function() {
		let tooltip = tooltipList[this.attributes.for.value];
		tooltip.style.display = 'block';
	},
	'hide':function() {
		if (forceShow === true) return;
		let tooltip = tooltipList[this.attributes.for.value];
		tooltip.style.display = 'none';
	}
};


let performShowTips = function() {
	forceShow = !forceShow;
	Object.keys(tooltipList).forEach(function(tip) {
		tooltipList[tip].style.display = 'block';
	});
};

let performOverlayClose = function() {
	overlayId.style.display = 'none';
};

let assignTooltipOpen = function(label, tooltip) {
	label.style.cursor = 'pointer';

	Object.keys(tooltipEvents).forEach(function(eventType) {
		tooltipEvents[eventType].forEach(function(event) {
			label.addEventListener(event, tooltipControls[eventType], false);
		});
	});
};

let assignPageEvents = function() {
	// Add click event to close alert
	if (overlayCloseId){
		overlayCloseId.addEventListener('click', performOverlayClose, false);
	}

	// Toggle to show all tooltips
	if (showAllTooltips) {
		showAllTooltips.addEventListener('click', performShowTips, false);
	}

	for (let i = 0; i < tooltips.length; i++) {
		let tooltip = tooltips[i];

		if (!tooltip.attributes.for) {
			console.log('No for attribute found!');
			continue;
		}

		let tooltipFor = tooltip.attributes.for.value;
		let tooltipLabel = document.querySelector('label[for="' + tooltipFor + '"]');

		tooltipList[tooltipFor] = tooltip;

		assignTooltipOpen(tooltipLabel, tooltip);
	}
};

window.onload = assignPageEvents;