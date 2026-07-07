// App settings default
let appSettings = {
	appTheme: 'light',
	appSidebar: 'full',
	appColor: 'blue',
};

// Update settings
function setAppSettings(newSettings = {}) {
	appSettings = {
		...appSettings,
		...newSettings
	};
	applySettings();
}


// Initialize
document.addEventListener("DOMContentLoaded", applySettings);
window.setAppSettings = setAppSettings;