document.addEventListener("DOMContentLoaded", () => {
  const sidebar = document.querySelector("#app-sidebar")
  const backdrop = document.querySelector("[data-sidebar-backdrop]")
  const openButton = document.querySelector("[data-sidebar-toggle]")
  const closeButton = document.querySelector("[data-sidebar-close]")

  if (!sidebar) {
    return
  }

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
    if (sidebar.classList.contains("-translate-x-full")) {
      openSidebar()
      return
    }
    closeSidebar()
  })

  closeButton?.addEventListener("click", closeSidebar)
  backdrop?.addEventListener("click", closeSidebar)

  window.addEventListener("resize", () => {
    if (window.innerWidth >= 1024) {
      backdrop?.classList.add("hidden")
      openButton?.setAttribute("aria-expanded", "false")
    }
  })

  document.body.addEventListener("htmx:afterSwap", () => {
    if (window.HSStaticMethods && typeof window.HSStaticMethods.autoInit === "function") {
      window.HSStaticMethods.autoInit()
    }
  })
})
