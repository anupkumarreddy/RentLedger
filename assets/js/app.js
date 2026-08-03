document.addEventListener("DOMContentLoaded", () => {
  // ---------------------------------------------------------------------------
  // Legacy custom sidebar (no-op when the Preline overlay sidebar is used).
  // ---------------------------------------------------------------------------
  const sidebar = document.querySelector("#app-sidebar")
  const backdrop = document.querySelector("[data-sidebar-backdrop]")
  const openButton = document.querySelector("[data-sidebar-toggle]")
  const closeButton = document.querySelector("[data-sidebar-close]")

  if (sidebar) {
    const closeSidebar = () => {
      sidebar.classList.add("-translate-x-full")
      backdrop?.classList.add("hidden")
      openButton?.setAttribute("aria-expanded", "false")
    }
    const openSidebar = () => {
      sidebar.classList.remove("-translate-x-full")
      backdrop?.classList.remove("hidden")
      openButton?.setAttribute("aria-expanded", "true")
    }
    openButton?.addEventListener("click", () => {
      sidebar.classList.contains("-translate-x-full") ? openSidebar() : closeSidebar()
    })
    closeButton?.addEventListener("click", closeSidebar)
    backdrop?.addEventListener("click", closeSidebar)
    window.addEventListener("resize", () => {
      if (window.innerWidth >= 1024) {
        backdrop?.classList.add("hidden")
        openButton?.setAttribute("aria-expanded", "false")
      }
    })
  }

  // ---------------------------------------------------------------------------
  // htmx modal controller. Forms are fetched into #modal-root via hx-get.
  // ---------------------------------------------------------------------------
  const modalRoot = document.getElementById("modal-root")

  const closeModal = () => {
    if (!modalRoot) return
    modalRoot.innerHTML = ""
    document.body.classList.remove("overflow-hidden")
  }

  if (modalRoot) {
    // Clicking the dimmed backdrop (but not the card) closes the modal.
    modalRoot.addEventListener("click", (event) => {
      if (event.target.matches("[data-modal-overlay]")) closeModal()
      if (event.target.closest("[data-modal-close]")) closeModal()
    })

    // Lock/unlock page scroll as modal content is injected or cleared.
    document.body.addEventListener("htmx:afterSwap", (event) => {
      if (event.detail.target && event.detail.target.id === "modal-root") {
        const hasContent = modalRoot.children.length > 0
        document.body.classList.toggle("overflow-hidden", hasContent)
        if (hasContent) {
          const firstField = modalRoot.querySelector("input, select, textarea")
          firstField?.focus()
        }
      }
    })
  }

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") closeModal()
  })

  // Re-init any Preline widgets inside htmx-swapped content.
  document.body.addEventListener("htmx:afterSwap", () => {
    if (window.HSStaticMethods && typeof window.HSStaticMethods.autoInit === "function") {
      window.HSStaticMethods.autoInit()
    }
  })
})
