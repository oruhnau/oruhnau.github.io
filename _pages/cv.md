---
layout: page
permalink: /cv/
title: CV
nav: true
nav_order: 4
description: Curriculum vitae of Oliver Ruhnau, Assistant Professor of Energy Market Design at the University of Cologne.
_styles: |
  .cv-actions {
    display: flex;
    flex-wrap: wrap;
    gap: 0.75rem;
    margin: 0 0 1.25rem 0;
  }
  .cv-button {
    display: inline-block;
    padding: 0.45rem 1rem;
    border: 1px solid var(--global-theme-color);
    border-radius: 0.3rem;
    color: var(--global-theme-color);
    text-decoration: none;
  }
  .cv-button:hover {
    background-color: var(--global-theme-color);
    color: var(--global-bg-color);
    text-decoration: none;
  }
  .cv-viewer {
    display: block;
    width: 100%;
    height: 90vh;
    min-height: 600px;
    border: 1px solid var(--global-divider-color);
  }
  /* Phones mostly cannot show an embedded PDF (or only its first page): use the buttons instead. */
  @media (max-width: 767px) {
    .cv-viewer {
      display: none;
    }
  }
---

<!-- The PDF is built from _data/cv.yml and _bibliography/papers.bib by bin/build_cv.py. -->
<!-- The ?v= suffix changes with every build, so browsers do not show a cached old version. -->

{% capture cv_pdf %}{{ '/assets/pdf/Oliver_Ruhnau_CV.pdf' | relative_url }}?v={{ site.time | date: '%s' }}{% endcapture %}

<div class="cv-actions">
  <a class="cv-button" href="{{ cv_pdf }}" download="Oliver_Ruhnau_CV.pdf"><i class="fa-solid fa-download"></i> Download PDF</a>
  <a class="cv-button" href="{{ cv_pdf }}" target="_blank" rel="noopener"><i class="fa-solid fa-up-right-from-square"></i> Open in new tab</a>
</div>

<object class="cv-viewer" data="{{ cv_pdf }}#view=FitH" type="application/pdf" aria-label="CV of Oliver Ruhnau (PDF)">
  <p>Your browser cannot display the PDF here. Please <a href="{{ cv_pdf }}">download the CV</a> instead.</p>
</object>
