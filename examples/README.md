# Synthetic notebook input

[vgsales.synthetic.csv](vgsales.synthetic.csv) contains 12 invented records created for this coursework repository. It is not an extract of a real sales dataset. Franchise prefixes are included solely to exercise the notebook's existing prefix matching; the game names, publishers and numbers are illustrative, not claims about real games.

The CSV uses the notebook's expected header and column order. It includes all four recognized franchise prefixes, the `2600` platform label, rows for the hardcoded analysis year 2016, `N/A` years, and one empty regional-sales value. Regional sales sum to Global_Sales in these examples, treating the missing regional value as zero solely for that arithmetic check. The notebook retains the missing value as null; decide a missing-value policy before analysing real data. Sales numbers are arbitrary illustrative units.

## Use in Databricks

1. Upload the CSV to an authorized Unity Catalog Volume, for example `/Volumes/<catalog>/<schema>/<volume>/examples/vgsales.synthetic.csv`.
2. Set the notebook's `input_csv` widget to that uploaded file path.
3. Set `output_dir` to a fresh directory outside the input directory, such as `/Volumes/<catalog>/<schema>/<volume>/results/synthetic-run-01`.
4. Run notebook cells in order. Expected inspection points: 12 input rows, Rank preserved as integers 1–12, `2600` normalized to `Atari 2600`, and the top-ten query returning source ranks 1–10. The missing regional value remains null. These are expected outcomes, not a recorded execution.

The source checkout's `examples/` path is not automatically available to a Databricks cluster. No local Spark runtime or cloud resources are bundled. This fixture demonstrates input shape and edge cases; it is too small and artificial for statistical conclusions or model evaluation. It does not validate the unrelated Cars, Spotify, movie, UFO or SalesLT datasets.
