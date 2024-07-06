import logging
from config.config import *
from google.cloud.bigquery_reservation_v1.services import reservation_service
from google.cloud.bigquery_reservation_v1.types import (
    reservation as reservation_types,
)


location = "US"
transport = "grpc"
reservation_name = None
assignment_name = None
reservation_client = None


def create_reservation():
    global reservation_name
    global reservation_client

    try:
        # Initialize the client
        reservation_client = reservation_service.ReservationServiceClient(
            transport=transport, credentials=credentials
        )

        # Create a reservation
        parent = reservation_client.common_location_path(project_id, location)
        reservation = reservation_types.Reservation(slot_capacity=slot_capacity)
        response = reservation_client.create_reservation(
            parent=parent, reservation_id=reservation_id, reservation=reservation
        )
        reservation_name = response.name
        logging.info(f"Created reservation: {reservation_name}")
    except Exception as e:
        if str(e) == f"409 An active reservation {reservation_id} already exists":
            logging.info(f"Reservation {reservation_id} already exists. Deleting it.")
            delete_reservation()
            create_reservation()


def create_reservation_assignment():
    global reservation_name
    global assignment_name
    global reservation_client

    logging.info(f"reservation_name: {reservation_name}")

    reservation_assignment = reservation_types.Assignment(
        job_type="QUERY", assignee=f"projects/{project_id}"
    )
    logging.info(f"reservation_assignment: {reservation_assignment}")

    response = reservation_client.create_assignment(
        parent=reservation_name, assignment=reservation_assignment
    )
    assignment_name = response.name


def delete_reservation():
    global reservation_client

    try:
        name = reservation_client.reservation_path(project_id, location, reservation_id)
        reservation_client.delete_reservation(name=name)
        logging.info("Deleted reservation: {}".format(name))
    except Exception as e:
        if "Cannot delete reservation with assignments" in str(e):
            logging.info(
                f"Reservation {reservation_id} has assignments. Deleting them."
            )
            delete_assignment()
            delete_reservation()


def delete_assignment():
    global assignment_name
    global reservation_client

    parent = f"projects/{project_id}/locations/{location}/reservations/{reservation_id}"
    assignments = reservation_client.list_assignments(parent=parent)

    for assignment in assignments:
        logging.info(f"Deleting assignment: {assignment.name}")
        reservation_client.delete_assignment(name=assignment.name)
        logging.info(f"Deleted assignment: {assignment.name}")
