// Utility function to fix modal scrolling issues
export const fixModalScrolling = () => {
  // Find all modal containers
  const modalContainers = document.querySelectorAll('.fixed.inset-0.bg-black\\/50.flex.items-center.justify-center.z-50 > div');
  
  modalContainers.forEach(container => {
    // Ensure the container has flex layout
    container.style.display = 'flex';
    container.style.flexDirection = 'column';
    container.style.maxHeight = '90vh';
    container.style.overflow = 'hidden';
    
    // Find the content area (usually the last div with padding)
    const contentArea = container.querySelector('div:last-child');
    if (contentArea && !contentArea.classList.contains('border-b')) {
      contentArea.style.flex = '1';
      contentArea.style.overflowY = 'auto';
      contentArea.style.overflowX = 'hidden';
    }
  });
};

// Auto-fix when DOM changes
export const initModalScrollFix = () => {
  // Use MutationObserver to watch for modal additions
  const observer = new MutationObserver((mutations) => {
    mutations.forEach((mutation) => {
      if (mutation.type === 'childList') {
        mutation.addedNodes.forEach((node) => {
          if (node.nodeType === Node.ELEMENT_NODE) {
            if (node.classList && node.classList.contains('fixed')) {
              // Small delay to ensure modal is fully rendered
              setTimeout(fixModalScrolling, 100);
            }
          }
        });
      }
    });
  });

  observer.observe(document.body, {
    childList: true,
    subtree: true
  });

  // Also fix on window resize
  window.addEventListener('resize', fixModalScrolling);
  
  return observer;
};
