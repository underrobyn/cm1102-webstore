let performOverlayClose = function() {
	let overlayId = document.getElementById('alerts');

	overlayId.style.display = "none";
};

let allowOverlayClose = function() {
	let overlayCloseId = document.getElementById('close_alert');

	overlayCloseId.addEventListener('click', performOverlayClose, false);
};

window.onload = allowOverlayClose;