---
layout: page
permalink: /research/
title: Research
nav: true
nav_order: 2
_styles: |
  .post-title {
    display: none;
  }
  /* Same space above a section heading as below it (the theme gives lists 2rem on top). */
  .publications + h2 {
    margin-top: 2rem;
  }
---

<!-- _pages/publications.md -->

<h2>Journal articles</h2>

<div class="publications">

{% bibliography --query @article %}

</div>

<h2>Working papers</h2>

<div class="publications">

{% bibliography --query @unpublished %}

</div>

<h2>Conference proceedings & book chapters</h2>

<div class="publications">

{% bibliography --query @*[keywords~=proceedings] %}

</div>

<h2>Software & data</h2>

<div class="publications">

{% bibliography --query @*[keywords~=software] %}

</div>
