/**
 * Sistema centralizado de Sweet Alerts para FortiFlow
 * Maneja todos los mensajes de éxito, error y confirmación del proyecto
 */

class SweetAlertManager {
    constructor() {
        this.isProcessing = false;
        this.lastMessageTime = 0;
        this.lastMessageText = '';
        this.init();
    }

    init() {
        // Escuchar eventos HTMX globalmente
        document.body.addEventListener('htmx:afterOnLoad', (evt) => {
            this.handleHTMXResponse(evt);
        });

        // Escuchar eventos personalizados
        document.body.addEventListener('showSuccess', (evt) => {
            this.showSuccess(evt.detail);
        });

        document.body.addEventListener('showError', (evt) => {
            this.showError(evt.detail);
        });

        document.body.addEventListener('showConfirm', (evt) => {
            this.showConfirm(evt.detail);
        });
    }

    // Manejar respuestas HTMX automáticamente
    handleHTMXResponse(evt) {
        // Prevenir procesamiento duplicado
        if (this.isProcessing) return;
        
        const status = evt.detail.xhr.status;
        const headers = evt.detail.xhr.getAllResponseHeaders();
        const successMessage = evt.detail.xhr.getResponseHeader('X-Success-Message');
        const errorMessage = evt.detail.xhr.getResponseHeader('X-Error-Message');
        const formElement = evt.detail.elt;
        
        // Solo procesar respuestas exitosas con mensajes
        if (status === 204 && successMessage) {
            // Obtener información del contexto
            const context = this.getContextFromForm(formElement);
            
            this.showSuccess({
                title: this.getSuccessTitle(context.action, context.entity),
                text: successMessage,
                context: context
            });
        } else if (status >= 400 && errorMessage) {
            this.showError({
                title: 'Error',
                text: errorMessage
            });
        }
    }

    // Obtener contexto del formulario
    getContextFromForm(formElement) {
        if (!formElement) return { action: 'unknown', entity: 'unknown' };

        const formType = formElement.dataset.formType || '';
        const formId = formElement.id || '';
        
        // Extraer acción y entidad del tipo de formulario
        const [entity, action] = formType.split('-') || ['unknown', 'unknown'];
        
        return {
            action: action || 'unknown',
            entity: entity || 'unknown',
            formType: formType,
            formId: formId,
            targetId: formElement.getAttribute('hx-target')
        };
    }

    // Generar título de éxito basado en contexto
    getSuccessTitle(action, entity) {
        const entityNames = {
            'client': 'Cliente',
            'contract': 'Contrato',
            'user': 'Usuario',
            'portfolio': 'Portfolio',
            'debtor': 'Deudor',
            'obligation': 'Obligación',
            'assignment': 'Asignación',
            'program': 'Programa',
            'management': 'Gestión'
        };

        const actionNames = {
            'create': 'creado',
            'edit': 'editado',
            'update': 'actualizado',
            'delete': 'eliminado'
        };

        const entityName = entityNames[entity] || entity;
        const actionName = actionNames[action] || action;

        return `${entityName} ${actionName}`;
    }

    // Mostrar Sweet Alert de éxito
    showSuccess(options = {}) {
        if (this.isProcessing) return;
        
        const now = Date.now();
        const message = options.text || 'Operación realizada exitosamente.';
        
        // Prevenir mensajes duplicados en un período corto de tiempo
        if (now - this.lastMessageTime < 2000 && this.lastMessageText === message) {
            return;
        }
        
        this.lastMessageTime = now;
        this.lastMessageText = message;
        this.isProcessing = true;
        
        // Cerrar todos los modales primero
        this.closeAllModals();

        setTimeout(() => {
            // Remover Sweet Alerts existentes
            const existingSwal = document.querySelector('.swal2-container');
            if (existingSwal) {
                existingSwal.remove();
            }

            Swal.fire({
                title: options.title || '¡Éxito!',
                text: options.text || 'Operación realizada exitosamente.',
                icon: 'success',
                confirmButtonText: options.confirmButtonText || 'OK',
                allowOutsideClick: false,
                allowEscapeKey: false,
                heightAuto: false,
                backdrop: true,
                customClass: {
                    container: 'swal-global-success',
                    popup: 'swal-global-success'
                },
                didOpen: () => {
                    this.forceHighZIndex();
                },
                didClose: () => {
                    this.isProcessing = false;
                }
            }).then(() => {
                this.isProcessing = false;
                
                // Ejecutar callback después del éxito si existe
                if (options.onSuccess) {
                    options.onSuccess();
                }
                
                // Cerrar modales y recargar tablas según el contexto
                if (options.context) {
                    this.handlePostSuccessActions(options.context);
                }
            });
        }, 300);
    }

    // Mostrar Sweet Alert de error
    showError(options = {}) {
        Swal.fire({
            title: options.title || 'Error',
            text: options.text || 'Ha ocurrido un error.',
            icon: 'error',
            confirmButtonText: options.confirmButtonText || 'OK',
            customClass: {
                container: 'swal-global-error'
            }
        });
    }

    // Mostrar Sweet Alert de confirmación
    showConfirm(options = {}) {
        return Swal.fire({
            title: options.title || '¿Estás seguro?',
            text: options.text || 'Esta acción no se puede deshacer.',
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#d33',
            cancelButtonColor: '#3085d6',
            confirmButtonText: options.confirmButtonText || 'Sí, continuar',
            cancelButtonText: options.cancelButtonText || 'Cancelar'
        });
    }

    // Cerrar todos los modales
    closeAllModals() {
        const modals = document.querySelectorAll('.modal');
        modals.forEach(modal => {
            if (modal.open) {
                modal.close();
            }
        });
    }

    // Forzar z-index alto para Sweet Alert
    forceHighZIndex() {
        const swalContainer = document.querySelector('.swal2-container');
        if (swalContainer) {
            swalContainer.style.zIndex = '999999';
        }
        const swalPopup = document.querySelector('.swal2-popup');
        if (swalPopup) {
            swalPopup.style.zIndex = '999999';
        }
    }

    // Manejar acciones posteriores al éxito
    handlePostSuccessActions(context) {
        setTimeout(() => {
            // Cerrar modales según el tipo de entidad
            this.closeRelevantModal(context);
            
            // Recargar tablas
            this.reloadRelevantTable(context);
            
            // Lógica especial para contratos
            if (context.entity === 'contract' && context.action === 'create') {
                this.handleContractPostCreate();
            }
        }, 200);
    }

    // Lógica especial para después de crear contrato
    handleContractPostCreate() {
        setTimeout(() => {
            if (typeof list_contract_modal !== 'undefined') {
                list_contract_modal.showModal();
            }
        }, 400);
    }

    // Cerrar modal relevante según el contexto
    closeRelevantModal(context) {
        const { entity, action } = context;
        
        try {
            // Mapeo de entidades a modales
            const modalMap = {
                'client': {
                    'create': () => typeof add_client_modal !== 'undefined' && add_client_modal.close(),
                    'edit': () => typeof edit_client_modal !== 'undefined' && edit_client_modal.close()
                },
                'user': {
                    'create': () => typeof add_user_modal !== 'undefined' && add_user_modal.close(),
                    'edit': () => typeof edit_user_modal !== 'undefined' && edit_user_modal.close()
                },
                'portfolio': {
                    'create': () => typeof add_portfolio_modal !== 'undefined' && add_portfolio_modal.close(),
                    'edit': () => typeof edit_portfolio_modal !== 'undefined' && edit_portfolio_modal.close()
                },
                'debtor': {
                    'create': () => typeof add_debtor_modal !== 'undefined' && add_debtor_modal.close(),
                    'edit': () => typeof edit_debtor_modal !== 'undefined' && edit_debtor_modal.close()
                },
                'obligation': {
                    'create': () => typeof add_obligation_modal !== 'undefined' && add_obligation_modal.close(),
                    'edit': () => typeof edit_obligation_modal !== 'undefined' && edit_obligation_modal.close()
                },
                'management': {
                    'create': () => typeof add_management_modal !== 'undefined' && add_management_modal.close(),
                    'edit': () => typeof edit_management_modal !== 'undefined' && edit_management_modal.close()
                },
                'assignment': {
                    'create': () => typeof add_assignment_modal !== 'undefined' && add_assignment_modal.close(),
                    'edit': () => typeof edit_assignment_modal !== 'undefined' && edit_assignment_modal.close()
                },
                'contract': {
                    'create': () => {
                        if (typeof create_contract_modal !== 'undefined') create_contract_modal.close();
                        if (typeof list_contract_modal !== 'undefined') list_contract_modal.close();
                    },
                    'edit': () => typeof edit_contract_modal !== 'undefined' && edit_contract_modal.close()
                }
            };

            const entityModals = modalMap[entity];
            if (entityModals && entityModals[action]) {
                entityModals[action]();
            }
        } catch (error) {
            console.warn('Error closing modal:', error);
        }
    }

    // Recargar tabla relevante según el contexto  
    reloadRelevantTable(context) {
        const { entity } = context;
        
        // Mapeo de entidades a elementos de tabla para recargar
        const tableMap = {
            'client': '#tabla-clientes',
            'user': '#tabla-usuarios', 
            'portfolio': ['#tabla-portfolios', '#tabla-portafolio-general'], // Soporte para múltiples tablas
            'debtor': '#tabla-deudores',
            'obligation': '#tabla-obligaciones',
            'management': '#tabla-managements',
            'assignment': '#tabla-asignaciones',
            'contract': '#lista-contratos'
        };

        // Manejar tanto strings individuales como arrays de selectores
        const tableSelectors = Array.isArray(tableMap[entity]) ? tableMap[entity] : [tableMap[entity]];
        
        tableSelectors.forEach(tableSelector => {
            if (tableSelector && document.querySelector(tableSelector)) {
                // Solo trigger si el elemento existe en la página actual
                htmx.trigger(tableSelector, 'reload-table');
            }
        });
        
        // También trigger en body como fallback
        htmx.trigger(document.body, 'reload-table');
    }

    // Reabrir modal relevante después del éxito (legacy)
    reopenRelevantModal(context) {
        setTimeout(() => {
            if (context.formType.includes('contract')) {
                if (typeof list_contract_modal !== 'undefined') {
                    list_contract_modal.showModal();
                    // Recargar la lista de contratos
                    const clientId = this.extractClientIdFromContext(context);
                    if (clientId) {
                        htmx.ajax('GET', `/clients/contract/list/${clientId}/`, {
                            target: '#lista-contratos',
                            swap: 'innerHTML'
                        });
                    }
                }
            }
            // Agregar más lógica para otros tipos de modales según necesidad
        }, 200);
    }

    // Extraer ID de cliente del contexto (helper)
    extractClientIdFromContext(context) {
        // Lógica para extraer el client ID si es necesario
        // Esto puede variar según tu implementación
        return null;
    }
}

// Instanciar el manager globalmente (solo una vez)
if (!window.sweetAlertManager) {
    window.sweetAlertManager = new SweetAlertManager();
}

// Funciones de conveniencia globales
window.showSuccess = (options) => {
    window.sweetAlertManager.showSuccess(options);
};

window.showError = (options) => {
    window.sweetAlertManager.showError(options);
};

window.showConfirm = (options) => {
    return window.sweetAlertManager.showConfirm(options);
};

// Estilos CSS globales para Sweet Alert
const globalSweetAlertStyles = document.createElement('style');
globalSweetAlertStyles.textContent = `
    /* Sweet Alert z-index global */
    .swal2-container {
        z-index: 999999 !important;
    }
    .swal2-popup {
        z-index: 999999 !important;
    }
    .swal-global-success,
    .swal-global-error {
        z-index: 999999 !important;
    }
    .swal2-backdrop-show {
        z-index: 999998 !important;
    }
`;
document.head.appendChild(globalSweetAlertStyles);
