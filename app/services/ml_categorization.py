import joblib
import os
import numpy as np
import logging
import re
from typing import Optional

class MLCategorizationService:
    def __init__(self, model_path='app/models/transaction_classifier.joblib', vectorizer_path='app/models/vectorizer.joblib'):
        try:
            # Check if model files exist
            if not os.path.exists(model_path):
                raise FileNotFoundError(f"Model file not found: {model_path}")
            if not os.path.exists(vectorizer_path):
                raise FileNotFoundError(f"Vectorizer file not found: {vectorizer_path}")

            # Load model and vectorizer
            self.model = joblib.load(model_path)
            self.vectorizer = joblib.load(vectorizer_path)
            self.logger = logging.getLogger(__name__)
            
            # Verify model and vectorizer are loaded correctly
            if not hasattr(self.model, 'predict') or not hasattr(self.model, 'predict_proba'):
                raise ValueError("Invalid model: missing required methods")
            if not hasattr(self.vectorizer, 'transform'):
                raise ValueError("Invalid vectorizer: missing transform method")
            
            # Verify model classes
            if not hasattr(self.model, 'classes_'):
                raise ValueError("Model missing classes_ attribute")
            if len(self.model.classes_) == 0:
                raise ValueError("Model has no classes defined")
                
            # Bill-specific patterns
            self.bill_patterns = [
                r'\bbill\b',
                r'\bpmt\b',
                r'\bpayment\b',
                r'\bcharge\b',
                r'\binvoice\b',
                r'\bstatement\b',
                r'\bdue\b',
                r'\batt\b',
                r'\btmobile\b',
                r'\bverizon\b',
                r'\bcomcast\b',
                r'\bspectrum\b',
                r'\bxfinity\b',
                r'\belectric\b',
                r'\bwater\b',
                r'\bgas\b',
                r'\binternet\b',
                r'\bphone\b',
                r'\bmobile\b',
                r'\bcable\b',
                r'\butility\b',
                r'\bservice\b',
                r'\bhealth\b',
                r'\binsurance\b',
                r'\bmedical\b',
                r'\bdental\b',
                r'\bvision\b',
                r'\bsubscription\b',
                r'\bmembership\b',
                r'\brent\b',
                r'\bmortgage\b',
                r'\blease\b'
            ]
            self.bill_pattern = re.compile('|'.join(self.bill_patterns), re.IGNORECASE)
            
            # Store and service patterns
            self.store_patterns = {
                'Supplies': [
                    r'\bHOME DEPOT\b',
                    r'\bHD\b',
                    r'\bLOWES\b',
                    r'\bGORDON FOOD\b',
                    r'\bOFFICE DEPOT\b',
                    r'\bSTAPLES\b',
                    r'\bUNITED HEALTH\b',
                    r'\bAMZN\b',
                    r'\bAMAZON\b',
                    r'\bTARGET\b',
                    r'\bTGT\b'
                ],
                'Food': [
                    r'\bGROCERY\b',
                    r'\bSUPERMARKET\b',
                    r'\bMARKET\b',
                    r'\bTRADER\b',
                    r'\bWHOLE FOODS\b',
                    r'\bSAFEWAY\b',
                    r'\bKROGER\b',
                    r'\bALBERTSONS\b',
                    r'\bFOOD LION\b',
                    r'\bPUBLIX\b',
                    r'\bCOSTCO\b',
                    r'\bWALMART\b',
                    r'\bWM\b',
                    r'\bSUPERCENTER\b',
                    r'\bINSTACART\b',
                    r'\bDOORDASH\b',
                    r'\bUBER\b',
                    r'\bLYFT\b',
                    r'\bTHE CROISSANT CORNER\b',
                    r'\bSQ\b',
                    r'\bEATS\b',
                    # Enhanced cafe and restaurant patterns
                    r'\bCAFE\b',
                    r'\bCOFFEE\b',
                    r'\bPERFECT CUP\b',
                    r'\bSTARBUCKS\b',
                    r'\bDUNKIN\b',
                    r'\bRESTAURANT\b',
                    r'\bDINING\b',
                    r'\bBISTRO\b'
                ],
                'Merchandise': [
                    r'\bETSY\b'
                ],
                'Subscriptions': [
                    r'\bNETFLIX\b',
                    r'\bHULU\b',
                    r'\bDISNEY\+\b',
                    r'\bDISNEY\*\b',
                    r'\bDISNEY\+\*\b',
                    r'\bDISNEY.*\b',
                    r'\bSPOTIFY\b',
                    r'\bADOBE\b',
                    r'\bMICROSOFT\b',
                    # Enhanced subscription patterns
                    r'\bSLACK\b',
                    r'\bSUBSCRIPTION\b',
                    r'\bMEMBERSHIP\b',
                    r'\bPREMIUM\b',
                    r'\bPRO\b',
                    r'\bPLUS\b',
                    r'\bAMAZON PRIME\b',
                    r'\bAPPLE\b',
                    r'\bGOOGLE\b',
                    r'\bZOOM\b',
                    r'\bDROPBOX\b',
                    r'\bCANVA\b'
                ],
                'Healthcare': [
                    r'\bCIGNA\b',
                    r'\bHEALTH\b',
                    r'\bMEDICAL\b',
                    r'\bDOCTOR\b',
                    r'\bDENTAL\b',
                    r'\bVISION\b',
                    r'\bINSURANCE\b',
                    r'\bBLUE CROSS\b',
                    r'\bAETNA\b',
                    r'\bKAISER\b',
                    r'\bUNITED HEALTH\b',
                    r'\bCOPAY\b',
                    r'\bCLINIC\b',
                    r'\bHOSPITAL\b'
                ],
                'Utilities': [
                    r'\bCOMCAST\b',
                    r'\bINTERNET\b'
                ],
                'Travel': [
                    r'\bPARKING\b',
                    r'\bAIRBNB\b',
                    r'\bEXPEDIA\b',
                    r'\bHOTEL\b',
                    r'\bMOTEL\b',
                    r'\bRESORT\b',
                    r'\bTRAVEL\b',
                    r'\bTRIP\b',
                    r'\bFLIGHT\b',
                    r'\bAIRLINE\b',
                    r'\bTAXI\b',
                    r'\bRIDE\b'
                ]
            }
            
            # Payment method patterns
            self.payment_patterns = [
                r'\bCASH APP\b',
                r'\bPP\b',
                r'\bPAYPAL\b',
                r'\bZELLE\b',
                r'\bVENMO\b',
                r'\bGOOGLE PAY\b',
                r'\bWIRE TRANSFER\b',
                r'\bCHECK\b'
            ]
            
            # Compile patterns
            self.store_patterns_compiled = {
                category: re.compile('|'.join(patterns), re.IGNORECASE)
                for category, patterns in self.store_patterns.items()
            }
            self.payment_pattern = re.compile('|'.join(self.payment_patterns), re.IGNORECASE)
            
            # Log successful initialization
            self.logger.info("[MLCategorization] Service initialized successfully")
            self.logger.info(f"[MLCategorization] Model classes: {self.model.classes_}")
        except Exception as e:
            self.logger.error(f"[MLCategorization] Error initializing service: {str(e)}")
            raise

    def _is_bill_transaction(self, description: str) -> bool:
        """Check if a transaction description matches bill patterns."""
        try:
            return bool(self.bill_pattern.search(description))
        except Exception as e:
            self.logger.error(f"[MLCategorization] Error checking bill pattern: {str(e)}")
            return False

    def _get_store_category(self, description: str) -> Optional[str]:
        """Check if a transaction description matches store patterns."""
        try:
            for category, pattern in self.store_patterns_compiled.items():
                if pattern.search(description):
                    return category
            return None
        except Exception as e:
            self.logger.error(f"[MLCategorization] Error checking store pattern: {str(e)}")
            return None

    def _is_payment_method(self, description: str) -> bool:
        """Check if a transaction description matches payment method patterns."""
        try:
            return bool(self.payment_pattern.search(description))
        except Exception as e:
            self.logger.error(f"[MLCategorization] Error checking payment pattern: {str(e)}")
            return False

    def categorize_descriptions(self, descriptions, original_categories=None, verbose=False):
        """Categorize transaction descriptions using the trained model."""
        if verbose:
            print(f"🤖 [ML DEBUG] categorize_descriptions called with {len(descriptions) if descriptions else 0} descriptions")
        
        if not descriptions:
            self.logger.warning("[MLCategorization] Empty descriptions list provided")
            if verbose:
                print("🤖 [ML DEBUG] Empty descriptions list")
            return []
            
        if not isinstance(descriptions, list):
            self.logger.error("[MLCategorization] Descriptions must be a list")
            if verbose:
                print("🤖 [ML DEBUG] Descriptions not a list")
            return []
            
        if original_categories and len(descriptions) != len(original_categories):
            self.logger.error("[MLCategorization] Mismatch between descriptions and original_categories lengths")
            if verbose:
                print("🤖 [ML DEBUG] Length mismatch between descriptions and original_categories")
            return []
            
        if verbose:
            print(f"🤖 [ML DEBUG] First 3 descriptions: {descriptions[:3]}")
            
        try:
            # Transform descriptions
            X = self.vectorizer.transform(descriptions)
            if verbose:
                print(f"🤖 [ML DEBUG] Vectorizer transform completed, shape: {X.shape}")
            
            if X.shape[0] == 0:
                self.logger.warning("[MLCategorization] Vectorizer returned empty matrix")
                if verbose:
                    print("🤖 [ML DEBUG] Empty vectorizer matrix")
                return []
                
            # Get predictions and probabilities
            predictions = self.model.predict(X)
            probabilities = self.model.predict_proba(X)
            
            if verbose:
                print(f"🤖 [ML DEBUG] Model predictions completed, got {len(predictions)} predictions")
                print(f"🤖 [ML DEBUG] First 3 predictions: {predictions[:3]}")
            
            if len(predictions) == 0 or len(probabilities) == 0:
                self.logger.warning("[MLCategorization] Model returned empty predictions")
                if verbose:
                    print("🤖 [ML DEBUG] Empty model predictions")
                return []
                
            # Get feature names
            feature_names = self.vectorizer.get_feature_names_out()
            
            # Process each transaction
            results = []
            for i, (desc, pred, probs) in enumerate(zip(descriptions, predictions, probabilities)):
                try:
                    # Initialize variables for this transaction
                    top_categories = []
                    
                    # Get original category if provided
                    original_category = original_categories[i] if original_categories else None
                    
                    # Get top features for this prediction
                    top_features = self._get_top_features(X[i], feature_names, pred)
                    
                    # Check for store-specific patterns first
                    store_category = self._get_store_category(desc)
                    
                    # Create explanation and determine category
                    if original_category and original_category.lower() in ['utilities', 'rent', 'insurance', 'subscriptions']:
                        explanation = f"Bill transaction - keeping original category: {original_category}"
                        category = original_category.lower()
                    elif store_category:
                        explanation = f"Store-specific pattern matched: {store_category}"
                        category = store_category.lower()
                    elif self._is_payment_method(desc):
                        # Keep original category for payment methods if it's not Misc
                        if original_category and original_category.lower() != 'misc':
                            explanation = f"Payment method - keeping original category: {original_category}"
                            category = original_category.lower()
                        else:
                            explanation = "Payment method transaction"
                            category = 'misc'
                    else:
                        # Get top 3 categories by probability
                        top_categories = []
                        for j, prob in enumerate(probs):
                            if prob > 0.1:  # Only include categories with >10% probability
                                try:
                                    category_name = self.model.classes_[j]
                                    top_categories.append((category_name, float(prob)))
                                except IndexError:
                                    continue
                        
                        # Sort by probability
                        top_categories.sort(key=lambda x: x[1], reverse=True)
                        
                        if verbose:
                            print(f"🤖 [ML DEBUG] Transaction {i}: '{desc[:30]}' - Top categories: {top_categories[:3]}")
                        
                        # Use highest probability category
                        if top_categories:
                            category = top_categories[0][0]
                            explanation = f"Top features: {', '.join(top_features[:3])}"
                            if verbose:
                                print(f"🤖 [ML DEBUG] Selected category: {category} with confidence {top_categories[0][1]:.3f}")
                        else:
                            category = 'misc'
                            explanation = "No high confidence predictions"
                            if verbose:
                                print(f"🤖 [ML DEBUG] No high confidence predictions, defaulting to misc")
                    
                    # Log the categorization only if prediction differs from original
                    if original_category and original_category.lower() != category.lower():
                        self.logger.info(f"[MLCategorization] Description: {desc} | Original: {original_category} | Predicted: {category}")
                    
                    result_item = {
                        'description': desc,
                        'original_category': original_category,
                        'predicted': category,
                        'confidence': top_categories[0][1] if top_categories else 0.0,
                        'top': top_categories[:3],
                        'explanation': explanation
                    }
                    results.append(result_item)
                    
                    if verbose and i < 3:  # Log first 3 results for debugging
                        print(f"🤖 [ML DEBUG] Result {i}: {result_item}")
                    
                except Exception as e:
                    self.logger.error(f"[MLCategorization] Error processing transaction {i}: {str(e)}")
                    # Add a default result for failed transactions
                    results.append({
                        'description': desc,
                        'original_category': original_categories[i] if original_categories else None,
                        'predicted': 'misc',
                        'confidence': 0.0,
                        'top': [('misc', 1.0)],
                        'explanation': f"Error in processing - defaulting to Misc: {str(e)}"
                    })
            
            if verbose:
                print(f"🤖 [ML DEBUG] Completed categorization: {len(results)} results returned")
                if results:
                    predicted_counts = {}
                    for r in results:
                        pred = r.get('predicted', 'unknown')
                        predicted_counts[pred] = predicted_counts.get(pred, 0) + 1
                    print(f"🤖 [ML DEBUG] Category distribution: {predicted_counts}")
            
            return results
            
        except Exception as e:
            self.logger.error(f"[MLCategorization] Error in categorization: {str(e)}")
            if verbose:
                print(f"🤖 [ML DEBUG] Categorization error: {str(e)}")
            return []

    def _get_top_features(self, X, feature_names, pred):
        """Get top features for a given prediction."""
        try:
            if hasattr(self.model, 'coef_'):
                # For linear models (e.g., LogisticRegression)
                pred_idx = np.where(self.model.classes_ == pred)[0]
                if len(pred_idx) > 0:
                    feature_weights = X.toarray()[0] * self.model.coef_[pred_idx[0]]
                    top_feat_idx = np.argsort(np.abs(feature_weights))[::-1][:3]
                    return [feature_names[j] for j in top_feat_idx if X[0, j] > 0]
            return []
        except Exception as e:
            self.logger.error(f"[MLCategorization] Error getting top features: {str(e)}")
            return [] 