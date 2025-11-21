function deleteJob(jobId) {
    fetch("/delete-job", {
      method: "POST",
      body: JSON.stringify({ jobId: jobId }),
    }).then((_res) => {
      location.reload();
    });
  }