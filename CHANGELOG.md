## 2.1.0 (2023-09-22)

### Feat

- Deprecate normalize in favor of model_dump to align better with pydantic v2

### Refactor

- Remove model config from base Manifest class

## 2.0.0 (2023-07-13)

### Feat

- Update to support pydantic v2

## 1.4.1 (2023-06-17)

### Fix

- Fix none type values in Manifests

## 1.4.0 (2023-06-12)

### Feat

- Add support for pydantic models with non-dict roots

### Refactor

- Add method for loading from single file and add kwargs to to_file

## 1.3.0 (2023-06-11)

### Feat

- Add ability to modify a Manifest based on key values

### Refactor

- Allow passing Path types to file methods

## 1.2.1 (2023-06-11)

### Fix

- **types**: Fix typing on build-like classmethods in Manifest

## 1.2.0 (2023-06-10)

### Refactor

- Clean up expressions and remove excess lines

## 1.1.0 (2023-06-10)

### Feat

- Add support for relative paths in ref expression

## 1.0.3 (2023-06-09)
