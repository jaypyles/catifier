provider "google" {
    project     = "catifier"
    region      = "us-central1"
}

# GCS

resource "google_storage_bucket" "catifier_images" {
    name     = "catifier-images"
    location = "US"
}

# Service Account

resource "google_service_account" "catifier_service_account" {
    account_id   = "catifier-service-account"
    display_name = "Catifier Service Account"
}

resource "google_project_iam_member" "secret_accessor" {
    project = "catifier"
    role    = "roles/secretmanager.secretAccessor"
    member  = "serviceAccount:${google_service_account.catifier_service_account.email}"
}

resource "google_storage_bucket_iam_member" "storage_viewer" {
  bucket = google_storage_bucket.catifier_images.name
  role   = "roles/storage.legacyBucketReader"
  member = "serviceAccount:${google_service_account.catifier_service_account.email}"
}

resource "google_storage_bucket_iam_member" "catifier_images_object_admin" {
    bucket = google_storage_bucket.catifier_images.name
    role   = "roles/storage.objectAdmin"
    member = "serviceAccount:${google_service_account.catifier_service_account.email}"
}

# Cloud Run

# resource "google_cloud_run_service" "catifier_service" {
#     name     = "catifier-service"
#     location = "us-central1"
#     template {
#         spec {
#             containers {
#                 image = "docker.io/your-dockerhub-username/your-image-name:tag"
#             }
#             container_concurrency = 1
#         }
#     }
#     metadata {
#         annotations = {
#             "run.googleapis.com/service-account" = google_service_account.catifier_service_account.email
#         }
#     }
# }


