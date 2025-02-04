//use std::collections::HashMap;
//use wasm_bindgen::prelude::*;
//use std::sync::Mutex;
//use once_cell::sync::Lazy;
//use openmls::prelude::WireFormat;
use openmls::prelude::tls_codec::Deserialize;
use openmls::prelude::tls_codec::Serialize;
use openmls_basic_credential::SignatureKeyPair;
use openmls::prelude::CredentialWithKey;
use openmls::prelude::Ciphersuite;
use openmls::prelude::MlsGroup;
use openmls::prelude::BasicCredential;
use openmls::prelude::CredentialType;
use openmls::prelude::SignatureScheme;
use openmls::storage::OpenMlsProvider;
use openmls::prelude::KeyPackageBundle;
use openmls::prelude::KeyPackage;
use openmls_rust_crypto::OpenMlsRustCrypto;
use openmls::prelude::MlsGroupCreateConfig;
use openmls::prelude::MlsMessageIn;
use openmls::prelude::MlsMessageBodyIn;
use openmls::prelude::StagedWelcome;
use openmls::prelude::MlsGroupJoinConfig;




// A helper to create and store credentials.
fn generate_credential_with_key(
    identity: Vec<u8>,
    credential_type: CredentialType,
    signature_algorithm: SignatureScheme,
    provider: &impl OpenMlsProvider,
) -> (CredentialWithKey, SignatureKeyPair) {
    let credential = BasicCredential::new(identity);
    let signature_keys =
        SignatureKeyPair::new(signature_algorithm)
            .expect("Error generating a signature key pair.");

    // Store the signature key into the key store so OpenMLS has access
    // to it.
    signature_keys
        .store(provider.storage())
        .expect("Error storing signature keys in key store.");
     
    (
        CredentialWithKey {
            credential: credential.into(),
            signature_key: signature_keys.public().into(),
        },
        signature_keys,
    )
}

// A helper to create key package bundles.
fn generate_key_package(
    ciphersuite: Ciphersuite,
    provider: &impl OpenMlsProvider,
    signer: &SignatureKeyPair,
    credential_with_key: CredentialWithKey,
) -> KeyPackageBundle {
    // Create the key package
    KeyPackage::builder()
        .build(
            ciphersuite,
            provider,
            signer,
            credential_with_key,
        )
        .unwrap()
}

pub fn test0()
{


    // Define ciphersuite ...
    let ciphersuite: Ciphersuite = Ciphersuite::MLS_128_DHKEMX25519_AES128GCM_SHA256_Ed25519;
    // ... and the crypto provider to use.
    let provider = &OpenMlsRustCrypto::default();

    // Now let's create two participants.


    // First they need credentials to identify them
    let (sasha_credential_with_key, sasha_signer) = generate_credential_with_key(
        "Sasha".into(),
        CredentialType::Basic,
        ciphersuite.signature_algorithm(),
        provider,
    );

    let (maxim_credential_with_key, maxim_signer) = generate_credential_with_key(
        "Maxim".into(),
        CredentialType::Basic,
        ciphersuite.signature_algorithm(),
        provider,
    );

    // Then they generate key packages to facilitate the asynchronous handshakes
    // in MLS

    // Generate KeyPackages
    let maxim_key_package = generate_key_package(ciphersuite, provider, &maxim_signer, maxim_credential_with_key);

    // Now Sasha starts a new group ...
    let mut sasha_group = MlsGroup::new(
        provider,
        &sasha_signer,
        &MlsGroupCreateConfig::default(),
        sasha_credential_with_key,
    )
    .expect("An unexpected error occurred.");

    // ... and invites Maxim.
    // The key package has to be retrieved from Maxim in some way. Most likely
    // via a server storing key packages for users.
    let (mls_message_out, welcome_out, group_info) = sasha_group
        .add_members(provider, &sasha_signer, &[maxim_key_package.key_package().clone()])
        .expect("Could not add members.");

    // Sasha merges the pending commit that adds Maxim.
    sasha_group
    .merge_pending_commit(provider)
    .expect("error merging pending commit");

    // Sascha serializes the [`MlsMessageOut`] containing the [`Welcome`].
    let serialized_welcome = welcome_out
    .tls_serialize_detached()
    .expect("Error serializing welcome");

    // Maxim can now de-serialize the message as an [`MlsMessageIn`] ...
    let mls_message_in = MlsMessageIn::tls_deserialize(&mut serialized_welcome.as_slice())
    .expect("An unexpected error occurred.");

    // ... and inspect the message.
    let welcome = match mls_message_in.extract() {
    MlsMessageBodyIn::Welcome(welcome) => welcome,
    // We know it's a welcome message, so we ignore all other cases.
    _ => unreachable!("Unexpected message type."),
    };

    // Now Maxim can build a staged join for the group in order to inspect the welcome
    let maxim_staged_join = StagedWelcome::new_from_welcome(
        provider,
        &MlsGroupJoinConfig::default(),
        welcome,
        // The public tree is need and transferred out of band.
        // It is also possible to use the [`RatchetTreeExtension`]
        Some(sasha_group.export_ratchet_tree().into()),
    )
    .expect("Error creating a staged join from Welcome");

    // Finally, Maxim can create the group
    let mut maxim_group = maxim_staged_join
        .into_group(provider)
        .expect("Error creating the group from the staged join");

}


pub fn add(left: u64, right: u64) -> u64 {
    left + right
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn it_works() {
        let result = add(2, 2);
        assert_eq!(result, 4);
    }
}
