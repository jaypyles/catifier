resource "google_cloud_run_service" "catifier_service" {
  name     = "catifier-service"
  location = "us-central1"
  template {
    metadata {
      annotations = {
        "autoscaling.knative.dev/maxScale" = "1"
      }
    }
    spec {
      containers {
        image   = "docker.io/jpyles0524/catifier:latest"
        command = ["./start.sh"]
        ports {
          container_port = 8000
        }
      }
      container_concurrency = 1
    }
  }
  metadata {
    annotations = {
      "run.googleapis.com/service-account" = google_service_account.catifier_service_account.email
    }
  }
} 