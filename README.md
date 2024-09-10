# Crypto-glTF

This package implements adaptive, hierarchical encryption and decryption of 3D `.glTF` or `.glb` files.
It is suppprted for Python3.10 and above.

## Quickstart

### Install:

```
pip install crypto-gltf
```

### Loading a `.gltf` or `.glb` file:

```
from crypto_gltf import Asset

filepath = 'example/path/to/an/asset.glb'
asset = Asset.load(filepath)
```

### Encrypting an asset:

```
encryption_response = asset.encrypt()
```

### Exporting an encrypted asset:

```
save_directory = 'example/save/directory'
export_path = asset.save(save_directory)
```

### Accessing encryption keys:

```
encryption_key = encryption_response.key
k1 = key.k1
k2 = key.k2
k3 = key.k3
```

### Decrypting an asset:

Here k3 can be replaced by k1 or k2.
```
encrypted_asset = Asset,load(export_path)
encrypted_asset.decrypt(
    k3=encryption_response.key.k3,
)
encrypted_asset.save(save_directory)
```

## Advanced  Usage:

### Encrypting images:
```
mesh_and_image_encryption_response = asset.encrypt(encrypt_images=True)
```

### Configuring parameters:
```
configured_encryption_response = asset.encrypt(
    meshes_cipher_params=(1, 3, 10), #(p,q,r)
    images_cipher_params=(1, 1, 6), #(p,q,r)
    encrypt_images=True,
)
```

