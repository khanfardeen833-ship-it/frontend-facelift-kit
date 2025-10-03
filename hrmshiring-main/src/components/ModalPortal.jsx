import React from 'react';
import ReactDOM from 'react-dom';

const ModalPortal = ({ children, isOpen }) => {
  const modalRoot = document.getElementById('modal-root');
  
  if (!isOpen || !modalRoot) {
    return null;
  }

  return ReactDOM.createPortal(children, modalRoot);
};

export default ModalPortal;
