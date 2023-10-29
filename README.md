## Why this project exists: allowing for some things I don't think my static site generator supports

I build my websites with a static site generator called [Hugo](https://gohugo.io/). Even the newest versions of Hugo lack certain features (as far as I have been able to determine), features that I view as rather desriable. I have now implemented some of my wishlist, although there is still plenty more to do.

Making a separate preprocessor project like this has several advantages, as I see things:

- I can make things as quick-and-dirty as I like, without having to deal with the (completely reasonable) rigor that would be expected if I tried to implement things in a PR for the official hugo project. I'm doing this primarily for me (to automate a bunch of stuff in my content workflow), and this is simply the fastest way to make that happen. To be honest, I don't consider myself a hotshot dev (somewhat by choice -- I spend my time on enough other things I never will be, simply on account of my priorities), and thus don't really view a formal PR against the main hugo repo particularly realistic for me. All this to say, I very much appreciate the folks on whose shoulders I stand, but I am not one of them. I'll hack together what works for me and my circumstances, and post it publicly in the hope that it maybe helps someone else. I'll leave the impressive stuff to the folks who have the sort of impressive knowledge and time-commitment required to do it right.
- Building on the above point, I can make things work exactly how I want, without having to worry about the use cases and opinions of others. If I were trying to get all this integrated into the main project, this would not be the case.
- I am comfortable with Python and agree with many of its opinionated language choices, but have never used Go before. I would personally much rather maintain a large Python codebase than large Go codebase.

Right now this project only operates on Markdown hugo sites. I am eying moving my sites back to Org (if I move into Emacs full-time again), and if that happens, I'll probably make an effort to support both content formats.

## Things that have now been implemented

### Automatically building aggregation pages

There are advantages to keeping page size down. It is faster for users (smaller page sizes mean faster load times). It is generally easier to skim through a table of contents that only contains 5 things than one that contains 40. You get the idea.

However, it can also be useful to be able to skim through larger pages that are aggregations of content: sometimes you might want to be able to see the wider context of how things are laid out. To do that, you'll need to be able to see information about more than one page at a time.

Which content you smash together shouldn't be arbitrary, though. For the aggregation to make sense, it must help organize things for you in some semantically-useful way.

Rolling up collections of pages just makes sense in terms of searching and skimming. But we shouldn't have to do anything to make it happen. It should "just work."

### Automatically building HTML slides as an alternative text view of all content

Completely automated construction of markdown content slides based on page content (including an auto-generated TOC for the slideshow presentation, and proper translation of relevant Hugo shortcodes into HTML).

### Section-level (rather than page-level) subject-tagging of content

The construction of a subject index that is much more fine-grained than individual pages; supporting categorization tags for every single header on the site (vs. only at the page level). Hugo's Taxonomies (e.g., [here](https://www.jessicahuynh.info/blog/2020/06/hugo-taxonomies/)) let you set things up per-page using variables in the YAML/TOML frontmatter, but that's pretty useless for pages of substantial size (something that would equal tens of pages in print) where you'd want to subject-tag individual sections or subsections, for much more useful content navigation.

## Things that have not yet been implemented

### The ability to include some markdown content in other markdown content, no HTML or shortcodes necessary

Many people are probably thinking right about now "why not just use a normal quotation?" Good question. Quite simply, the answer is because the maintainability of hand-copied content is a nightmare, whereas if content is referenced programmatically, it will be updated completely automatically if it is changed in its source location.

I don't want to make a custom HTML shortcode every time I might want to include one piece of markdown content in more than one place. To be honest, I was kind of shocked that straight markdown-to-markdown referencing was not supported out-of-the-box. Anything other than that seems to me to be vastly more inefficient.

I want to do better than making standalone markdown blobs everywhere, though. No, I'd rather be able to seamlessly integrate already-existing content into a new page without even touching the old location. No refactoring should be necessary, and we shouldn't have any unnaturally broken-up content; stringing together smaller standalone markdown files to be re-used seems a lot less intuitive to me than just statically referencing content sections from another complete file that already exists.

Based on this, I want to define a specific API for including:

- An entire page
- A specific section of a page (referenced by header) -- without any nested subheaders
- A specific section of a page (referenced by header) -- including all nested subheaders
- Some range of content on a page (referenced inclusively by `fromHeader` through `toHeader` -- `toHeader` may be semantically under `fromHeader`, i.e., a subsection of `fromHeader`)

And then set up references to automatically include exactly the content I want, and have it update seamlessly *everywhere* whenever I update it in its source location.

Oh, and to make things robust, we need to elegantly handle when header names change too (make it easy to update references broken by renaming headers -- compare links breaking on the internet). It will be unavoidable, but we can make it less painful to deal with with some thought. At least I would imagine so.


<!--

#### 2) Searching

Let's say you have blog posts A, B, C, and D. All are dealing with slightly different facets of the same topic. For the sake of example, let's say the topic is electric bicycles, and these posts represent writing about several different classes of electric bikes.

Now let's say you know you wrote something about puncture-resistance in ebike tires on one of these pages, but you don't remember which one. While it is true that you *could* go search each individual page separately, that's 



However, it can be extremely useful to view and search through wider aggregations of content within the same general topical scope. Information is only useful to you if you can find it, after all. So what if, for all content, we also made it accessible on a wider aggregation page, grouped with like content, for the purpose of searching?

And further, what if we let users dynamically show and hide things relating to each page (such as the full content -- rather than just the title and summary and timestamps -- and the usually very-long video transcript) to make searching even more effective? That is, users would be able to search across all related pages on the following sets of data

- Just titles, summaries, and timestamps
- All of the above plus the full content (but no transcripts)
- All of the above plus transcripts (but no full content)
- All of the above plus the full content plus transcripts

Some people may be somewhat lost reading this, and that's fine. Not everyone will care. I'm building this particular feature for myself. It drives me crazy when I know I've written about something, but I can't simply find where.

Searching via search engine (e.g., `my search terms site:steventammen.com`) does work fine, but it suffers in one major aspect: it lacks full context in displaying results. That's no small disadvantage.

It's not just searching too. Skimming is something that is immensely useful for rapidly getting an idea of lots of information, and aggregating wider content like this empowers page skimming in a way that a large collection of separate pages does not. By skimming a collection of content with the full content and transcripts hidden (i.e., only showing titles, summaries, and timestamps), you can get an idea of things without getting bogged down, and then instantly expand things out if you decide you actually want the full treatment for some specific topic.

#### How big should the aggregation groups be? How does one create groups generally?

One might ask: why not just build a single webpage containing all site content and search on that? The answer is performance. A middle ground needs to be had between having a wide enough set of content that you can actually find all the references you are looking for, while at the same time not having a problematically large set of material to search through

While I may not generally remember exactly which page I wrote something on, as long as I organize my content relatively well, I should be able to get close.

Hence, larger than one page but smaller than all pages on the site. The lines get blurry in the in-between space. For example, a content type I am planning on publishing to on my personal website is called `random-ramblings`, and contains a bunch of random links from things I've researched


##### Things that follow set topics

Things that naturally form topic-based series lend themselves well to being aggregated that way. So I might do a series of reviews on backpacks, and then a page aggregating the backpack reviews. Or [a series of videos on teaching programming](N5KyJUu_VqG38oglZEEw17b_ZQ13On) and then [an aggregation page for the series](https://www.steventammen.com/pages/learning-programming-only-what-you-really-need/).

Things that tend to be organized by topic will just be grouped that way.

##### Things that do not follow set topics

These are more complicated. For me specifically, my daily progress summary vlogs and random ramblings (=my attempt to snapshot my half-organized thoughts on things in a rolling manner over time, similar-ish to blogging as it is conventionally defined) do not really track according to consistent topics.

That is, in the video for a certain day I might be talking about the engineering and design of electric bicycles, and then the next day may be going off on a completely unrelated tangent about microservices in web application deployment. The two things are not terribly related. So how do you aggregate these things?

I have chosen to do it by time.





I have plans to eventually make an aggregation page for the daily vlogs that I do. Having just one page for all time would eventually grow far too large to be useful, so instead I'll probably break it up by year. Same deal with the planned content type of `random-ramblings` that I have, which is more or less what I'm calling unstructured blog posts. I'll probably just have the aggregation for this be a yearly affair.

This works out well, because as a rule of thumb, while searching for stuff is always useful, human brains do operate on the principle of temporal proximity. That is to say, for those of us without eidetic memories, to a certain extent, our brains operate on the principle of out-of-sight

the probability of me wanting to find something I know I worked on is going to be heavily conditioned by how fresh it is in my mind. If I did something long enough ago, I may not remember many details ab










As long as it is not done deceptively, duplicate content does not inherently nuke SEO (quote [from Google](https://developers.google.com/search/docs/advanced/guidelines/duplicate-content#:~:text=in%20Search%20Console.-,Duplicate%20content%20on%20a,in%20our%20search%20results.,-However%2C%20if%20our))

> Duplicate content on a site is not grounds for action on that site unless it appears that the intent of the duplicate content is to be deceptive and manipulate search engine results. If your site suffers from duplicate content issues, and you don't follow the advice listed in this document, we do a good job of choosing a version of the content to show in our search results.

(The main disadvantage appears to be that you may just end up with the less-expected versions of your content being selected as the ones that ranks).






Duplicating content between leaf pages and a collection/aggregation page that allows for showing/hiding page content and video transcriptions for the purposes of advanced searching. My brief perusal of the SEO impact of such a practice has mostly been positive:


I still need to figure out how to do this without messing badly with SEO, but per Google's guidelines, the worst that may happen if I do absolutely nothing further is that sometimes the top result might end up an aggregation page instead of a leaf page. As long as all the traffic is still my site, I think I'm OK with that


In an ideal world, I'd learn Go, spend time understanding the Hugo codebase, and contribute pull requests to the open source project myself. But I need to operate within the confines of reality, and within those confines, I have a full time job, run two websites/YouTube channels, and so on. I

An understandable, extensible application for adding additional functionality to websites built with static site generators

-->
