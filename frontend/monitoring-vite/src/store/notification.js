let notificationState = {
    message: '',
    type: '',
    timeout: null,
  };
  
  function showNotification(message, type) {
    notificationState.message = message;
    notificationState.type = type;
  
    if (notificationState.timeout) {
      clearTimeout(notificationState.timeout);
    }
  
    notificationState.timeout = setTimeout(() => {
      clearNotification();
    }, 5000);
  }
  
  function clearNotification() {
    notificationState.message = '';
    notificationState.type = '';
    if (notificationState.timeout) {
      clearTimeout(notificationState.timeout);
      notificationState.timeout = null;
    }
  }
  
  export default {
    showNotification,
    clearNotification,
    getState: () => notificationState
  };
  