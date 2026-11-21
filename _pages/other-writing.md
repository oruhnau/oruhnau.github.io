---
layout: page
permalink: /other-writing/
title: Other writing
nav: true
nav_order: 3
_styles: |
  .post-title {
    display: none;
  }
  /* Same space above a section heading as below it (the theme gives lists 2rem on top). */
  .publications + h2 {
    margin-top: 2rem;
  }
---

<!-- _pages/other-writing.md: entries come from _bibliography/papers.bib, selected by their `keywords`. -->

<h2>Commissioned studies</h2>

<div class="publications">

{% bibliography --query @*[keywords~=report] %}

</div>

<h2>Commentaries</h2>

<div class="publications">

{% bibliography --query @*[keywords~=commentary] %}

</div>
