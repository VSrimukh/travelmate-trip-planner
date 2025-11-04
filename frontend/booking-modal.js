window.showBookingModal = function (serviceData) {
  const user = JSON.parse(
    localStorage.getItem("travelmate_current_user") || "null"
  );

  if (!user) {
    alert("Please login to book trips. Redirecting to login page...");
    setTimeout(() => {
      window.location.href = "login.html";
    }, 1000);
    return;
  }
  alert("Trip booked successfully!");
  const booking = {
    id: generateBookingId(serviceData.type),
    userId: user.id || "guest",
    type: serviceData.type || "service",
    title: serviceData.title || "Service Booking",
    from: serviceData.from || "",
    to: serviceData.to || "",
    date: new Date().toISOString(),
    travelDate: serviceData.date || "",
    time: serviceData.time || "",
    price: serviceData.price || "₹0",
    status: "confirmed",
    bookingTime: new Date().toISOString(),
  };

  const bookings = JSON.parse(
    localStorage.getItem("travelmate_bookings") || "[]"
  );
  bookings.push(booking);
  localStorage.setItem("travelmate_bookings", JSON.stringify(bookings));
};

function generateBookingId(type) {
  const prefix = type?.toUpperCase().substr(0, 2) || "BK";
  return `${prefix}${Date.now()}`;
}
