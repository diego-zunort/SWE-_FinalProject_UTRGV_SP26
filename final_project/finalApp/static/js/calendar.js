(() => {
  const calendarEl = document.getElementById("club-calendar");
  if (!calendarEl || !window.FullCalendar) return;

  const calendar = new FullCalendar.Calendar(calendarEl, {
    initialView: "dayGridMonth",
    height: "auto",
    headerToolbar: {
      left: "prev,next today",
      center: "title",
      right: "dayGridMonth,timeGridWeek,timeGridDay",
    },
    navLinks: true,
    eventTimeFormat: { hour: "numeric", minute: "2-digit", meridiem: "short" },
    events: async (fetchInfo, successCallback, failureCallback) => {
      try {
        const url = new URL(window.VENTURE_EVENTS_FEED_URL, window.location.origin);
        url.searchParams.set("start", fetchInfo.startStr);
        url.searchParams.set("end", fetchInfo.endStr);

        const response = await fetch(url.toString(), { headers: { Accept: "application/json" } });
        if (!response.ok) {
          failureCallback();
          return;
        }

        const data = await response.json();
        successCallback(data);
      } catch (error) {
        failureCallback(error);
      }
    },
    eventClick: (info) => {
      const targetUrl = info.event.url;
      if (!targetUrl) return;
      info.jsEvent.preventDefault();
      window.location.href = targetUrl;
    },
  });

  calendar.render();
})();
